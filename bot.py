"""最小记账 Bot：Telegram 收消息 -> 解析「牛肉面 35」-> 写入 SQLite -> 回复。
只用 Python 标准库。运行：TELEGRAM_BOT_TOKEN=xxx python3 bot.py
"""
import json
import os
import re
import sqlite3
import time
import urllib.parse
import urllib.request
from decimal import Decimal

DB_PATH = os.environ.get("LEDGER_DB", "ledger.db")
FAIL_REPLY = "没看懂，请按「项目 金额」发送，例如：牛肉面 35"

# 项目名必须以非数字结尾，金额最多两位小数，可带「元」「块」
PATTERN = re.compile(r"^\s*(.*?\D)\s*(\d+(?:\.\d{1,2})?)\s*(?:元|块)?\s*$")


def init_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id      INTEGER NOT NULL,
            item         TEXT    NOT NULL,
            amount_cents INTEGER NOT NULL,
            raw_text     TEXT    NOT NULL,
            created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )"""
    )
    conn.commit()


def parse(text):
    """返回 (项目, 金额分)，解析失败返回 None。"""
    m = PATTERN.match(text or "")
    if not m:
        return None
    item = m.group(1).strip()
    cents = int(Decimal(m.group(2)) * 100)
    if not item or cents <= 0:
        return None
    return item, cents


def handle(conn, chat_id, text):
    """处理一条消息，返回要回复的文字。解析失败不写库。"""
    parsed = parse(text)
    if parsed is None:
        return FAIL_REPLY
    item, cents = parsed
    conn.execute(
        "INSERT INTO expenses (chat_id, item, amount_cents, raw_text) VALUES (?, ?, ?, ?)",
        (chat_id, item, cents, text),
    )
    conn.commit()
    return f"已记账：{item} {cents / 100:.2f} 元"


def tg(token, method, **params):
    data = urllib.parse.urlencode(params).encode()
    url = f"https://api.telegram.org/bot{token}/{method}"
    with urllib.request.urlopen(url, data=data, timeout=40) as resp:
        return json.load(resp)


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    offset = 0
    print("bot started, db =", DB_PATH)
    while True:
        try:
            res = tg(token, "getUpdates", offset=offset, timeout=30)
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                text = msg.get("text")
                if text is None:
                    continue
                chat_id = msg["chat"]["id"]
                tg(token, "sendMessage", chat_id=chat_id, text=handle(conn, chat_id, text))
        except Exception as e:  # 网络抖动时不退出
            print("error:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
