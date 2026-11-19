"""首个验收用例。运行：python3 -m unittest -v"""
import sqlite3
import unittest

from bot import FAIL_REPLY, handle, init_db


class LedgerAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_db(self.conn)

    def rows(self):
        return self.conn.execute(
            "SELECT chat_id, item, amount_cents, raw_text FROM expenses"
        ).fetchall()

    def test_success(self):
        # 输入「牛肉面 35」-> 写入一行 -> 回复确认
        reply = handle(self.conn, 10001, "牛肉面 35")
        self.assertEqual(reply, "已记账：牛肉面 35.00 元")
        self.assertEqual(self.rows(), [(10001, "牛肉面", 3500, "牛肉面 35")])

    def test_variants(self):
        handle(self.conn, 1, "牛肉面35")
        handle(self.conn, 1, "奶茶 18.5元")
        self.assertEqual(
            [(r[1], r[2]) for r in self.rows()], [("牛肉面", 3500), ("奶茶", 1850)]
        )

    def test_fail_writes_nothing(self):
        # 解析失败 -> 不写库 -> 回复提示格式
        for bad in ["今天好累", "35", "牛肉面", "牛肉面 0", ""]:
            self.assertEqual(handle(self.conn, 1, bad), FAIL_REPLY)
        self.assertEqual(self.rows(), [])


if __name__ == "__main__":
    unittest.main()
