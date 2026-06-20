"""重新设置所有比赛截止时间为 kickoff - 5 分钟。"""
from datetime import timedelta
from app.db.database import SessionLocal
from app.db.models import Match

db = SessionLocal()
count = 0
for m in db.query(Match).all():
    if m.status == "ft":
        continue
    m.betting_close_at = m.kickoff_at - timedelta(minutes=5)
    count += 1
db.commit()
print(f"Updated {count} matches' close_at")
db.close()
