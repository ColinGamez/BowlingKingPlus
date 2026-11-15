import unittest

from tools.map_protocol import map_dump


class ProtocolMapTests(unittest.TestCase):
    def test_namespaces_keep_message_directions_distinct(self):
        dump = '''// Namespace: BowlingKingC2GS
public class Common // TypeDefIndex: 1
{
    public const RmiID RequestLogin = 3001;
}
// Namespace: BowlingKingGS2C
public class Common // TypeDefIndex: 2
{
    public const RmiID RequestLoginAck = 4001;
}
// Namespace: Other
public class Common // TypeDefIndex: 3
{
    public const RmiID IgnoreMe = 12;
}
// Namespace: 
public class BKApi // TypeDefIndex: 4
{
    // RVA: 0x1234 Offset: 0x1234 VA: 0x1234
    public void Login(string uid) { }
}
'''
        report = map_dump(dump.replace("\n", "\r\n"))
        self.assertEqual(report["message_count"], 2)
        self.assertEqual(report["messages"][0], {
            "namespace": "BowlingKingC2GS", "name": "RequestLogin", "id": 3001})
        self.assertEqual(report["messages"][1]["namespace"], "BowlingKingGS2C")
        self.assertEqual(report["research_targets"][0]["methods"], [
            {"rva": "0x1234", "signature": "public void Login(string uid)"}])

    def test_unrelated_dump_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "No Bowling King"):
            map_dump("unrelated input")
