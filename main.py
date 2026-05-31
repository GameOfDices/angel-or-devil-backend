from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import database, models

models.Base.metadata.create_all(bind=database.engine)

try:
    with database.engine.connect() as conn:
        conn.execute(text("ALTER TABLE submissions ALTER COLUMN score TYPE FLOAT USING score::float"))
        conn.commit()
except Exception:
    pass

limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://angel-or-devil.com",
        "https://www.angel-or-devil.com",
        "https://angel-or-devil.onrender.com",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class SubmitRequest(BaseModel):
    gender: str
    score: float
    sins: List[int]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
@limiter.limit("1/minute")
def submit(request: Request, data: SubmitRequest, db: Session = Depends(database.get_db)):
    if data.gender not in ("m", "f"):
        return {"error": "invalid gender"}
    sub = models.Submission(gender=data.gender, score=data.score, sins=data.sins)
    db.add(sub)
    db.commit()
    return {"ok": True}


@app.get("/stats")
def stats(db: Session = Depends(database.get_db)):
    rows = db.query(models.Submission).all()
    result = {
        "countM": 0, "countF": 0,
        "totalM": 0, "totalF": 0,
        "sins": {}
    }
    for row in rows:
        g = row.gender
        if g == "m":
            result["countM"] += 1
            result["totalM"] += row.score
        elif g == "f":
            result["countF"] += 1
            result["totalF"] += row.score
        for sin_id in row.sins:
            sid = str(sin_id)
            if sid not in result["sins"]:
                result["sins"][sid] = {"m": 0, "f": 0}
            result["sins"][sid][g] = result["sins"][sid].get(g, 0) + 1
    return result
