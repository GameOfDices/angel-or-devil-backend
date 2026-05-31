from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import database, models

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

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
    score: int
    sins: List[int]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
def submit(data: SubmitRequest, db: Session = Depends(database.get_db)):
    if data.gender not in ("m", "f", "d"):
        return {"error": "invalid gender"}
    sub = models.Submission(gender=data.gender, score=data.score, sins=data.sins)
    db.add(sub)
    db.commit()
    return {"ok": True}


@app.get("/stats")
def stats(db: Session = Depends(database.get_db)):
    rows = db.query(models.Submission).all()
    result = {
        "countM": 0, "countF": 0, "countD": 0,
        "totalM": 0, "totalF": 0, "totalD": 0,
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
        elif g == "d":
            result["countD"] += 1
            result["totalD"] += row.score
        for sin_id in row.sins:
            sid = str(sin_id)
            if sid not in result["sins"]:
                result["sins"][sid] = {"m": 0, "f": 0, "d": 0}
            result["sins"][sid][g] = result["sins"][sid].get(g, 0) + 1
    return result
