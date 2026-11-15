"""Disassemble an ELF virtual-address range, resolving conservative literal references.

Requires the optional packages in tools/requirements-research.txt.
Output stays local; annotations are references, not recovered request schemas.
"""

import argparse
import json
from pathlib import Path
import re


def main():
    from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
    from capstone.arm64 import ARM64_OP_IMM, ARM64_OP_MEM, ARM64_OP_REG
    from elftools.elf.elffile import ELFFile
    from elftools.elf.relocation import RelocationSection

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("elf", type=Path)
    parser.add_argument("start", type=lambda value: int(value, 0))
    parser.add_argument("end", type=lambda value: int(value, 0))
    parser.add_argument("--literals", type=Path)
    parser.add_argument("--dump", type=Path, help="Optional dump.cs for branch target names")
    args = parser.parse_args()
    if args.start < 0 or args.end <= args.start or args.end - args.start > 1024 * 1024:
        parser.error("provide an increasing address range of at most 1 MiB")
    literals = {}
    methods = {}
    if args.dump:
        dump = args.dump.read_text(encoding="utf-8-sig")
        methods = {int(address, 16): signature.strip() for address, signature in re.findall(
            r"// RVA: (0x[\dA-Fa-f]+)[^\n]*\n\s*([^\n]+\{ \})", dump)}
    if args.literals:
        literals = {int(item["address"], 16): item["value"] for item in
                    json.loads(args.literals.read_text(encoding="utf-8-sig"))}
    with args.elf.open("rb") as stream:
        elf = ELFFile(stream)
        if elf.get_machine_arch() != "AArch64":
            parser.error("input must be an AArch64 ELF")
        code = None
        for segment in elf.iter_segments():
            if (segment["p_type"] == "PT_LOAD" and segment["p_flags"] & 1
                    and segment["p_vaddr"] <= args.start
                    and args.end <= segment["p_vaddr"] + segment["p_filesz"]):
                stream.seek(segment["p_offset"] + args.start - segment["p_vaddr"])
                code = stream.read(args.end - args.start)
                break
        if code is None:
            parser.error("range is not inside one executable file-backed ELF segment")
        # AArch64 R_AARCH64_RELATIVE only; symbol relocations need different handling.
        relocations = {rel["r_offset"]: rel["r_addend"]
                       for section in elf.iter_sections() if isinstance(section, RelocationSection)
                       for rel in section.iter_relocations()
                       if rel.is_RELA() and rel["r_info_type"] == 1027}
    decoder = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    decoder.detail = True
    registers = {}
    for instruction in decoder.disasm(code, args.start):
        operands = instruction.operands
        value = None
        annotation = ""
        if instruction.mnemonic in ("bl", "b") and operands and operands[0].type == ARM64_OP_IMM:
            if operands[0].imm in methods:
                annotation = " ; " + methods[operands[0].imm]
        if instruction.mnemonic in ("adrp", "adr") and len(operands) == 2:
            value = operands[1].imm
        elif instruction.mnemonic == "add" and len(operands) == 3:
            if operands[1].type == ARM64_OP_REG and operands[2].type == ARM64_OP_IMM:
                base = registers.get(operands[1].reg)
                if base is not None and not operands[2].shift.value:
                    value = base + operands[2].imm
        elif instruction.mnemonic == "mov" and len(operands) == 2:
            if operands[1].type == ARM64_OP_REG:
                value = registers.get(operands[1].reg)
        elif instruction.mnemonic == "ldr" and len(operands) == 2 and operands[1].type == ARM64_OP_MEM:
            memory = operands[1].mem
            base = registers.get(memory.base)
            if base is not None and not memory.index:
                address = base + memory.disp
                value = relocations.get(address)
                target = value if value is not None else address
                if target in literals:
                    annotation = " ; literal reference " + json.dumps(literals[target], ensure_ascii=True)
        _, written = instruction.regs_access()
        for register in written:
            registers.pop(register, None)
            name = instruction.reg_name(register)
            if name.startswith("w") and name[1:].isdigit():
                # A write to Wn also replaces Xn; do not retain its former address.
                for known in list(registers):
                    if instruction.reg_name(known) == "x" + name[1:]:
                        registers.pop(known, None)
        if value is not None and operands and operands[0].type == ARM64_OP_REG:
            registers[operands[0].reg] = value
        print(f"0x{instruction.address:X}: {instruction.mnemonic} {instruction.op_str}{annotation}")
        # Avoid carrying guessed register values across calls or control-flow edges.
        if instruction.mnemonic in ("bl", "blr", "b", "br", "ret", "cbz", "cbnz", "tbz", "tbnz") or instruction.mnemonic.startswith("b."):
            registers.clear()


if __name__ == "__main__":
    main()
