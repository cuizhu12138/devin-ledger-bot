# devin-ledger-bot

最小可运行的记账 Bot：Telegram 收消息，解析「牛肉面 35」，写入 SQLite，回复确认。只用 Python 标准库，不用装依赖。

## 运行

```bash
python3 -m unittest -v                       # 跑验收用例，不需要 Token
TELEGRAM_BOT_TOKEN=你的token python3 bot.py   # 启动 Bot，数据写到 ledger.db
```

## 首个验收用例

| 输入 | 数据库写入（表 expenses） | Bot 回复 |
| --- | --- | --- |
| `牛肉面 35` | `chat_id=发送者, item='牛肉面', amount_cents=3500, raw_text='牛肉面 35', created_at=当前时间` | `已记账：牛肉面 35.00 元` |
| `今天好累` / `35` / `牛肉面` / `牛肉面 0` | 不写入 | `没看懂，请按「项目 金额」发送，例如：牛肉面 35` |

金额按「分」存整数，避免小数误差。也支持 `牛肉面35`、`奶茶 18.5元`。

## 后续

- 解析目前是正则；规则解析不了的再交给 LLM
- Todo、邮箱管理、转发到 Devin Session
