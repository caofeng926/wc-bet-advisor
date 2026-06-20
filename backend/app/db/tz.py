from datetime import datetime, timedelta

# 中国大陆默认使用 UTC+8（北京时间）。
# 为避免 SQLAlchemy 存入的 naive datetime 与 aware datetime 互操作报错，
# 这里返回 naive，调用者已经知道是北京时间。
BJ_OFFSET = timedelta(hours=8)

def now() -> datetime:
    """当前北京时间（naive datetime）"""
    return datetime.utcnow() + BJ_OFFSET
