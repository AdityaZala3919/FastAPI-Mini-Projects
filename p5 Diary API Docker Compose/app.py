from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os, json
from sqlalchemy import Column, Integer, String, Date

from database import Base, SessionLocal, engine

class DiaryIndex(Base):
    __tablename__ = "diary_index"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    json_path = Column(String, nullable=False)

# Create DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Internship Diary 2026")

DATA_DIR = "data"
EXPORT_DIR = "exports"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# ------------------ UTILITIES ------------------

def parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Date must be in DD-MM-YYYY format"
        )

def get_day_name(date_obj):
    return date_obj.strftime("%A")

# ------------------ ROUTES ------------------

@app.get("/")
def root():
    return RedirectResponse("/docs")

@app.post("/diary/")
def create_or_update_entry(date: str, text: str = None, todo: str = None):
    db = SessionLocal()

    try:
        parsed_date = parse_date(date)
        day_name = get_day_name(parsed_date)

        filename = f"{date}.json"
        filepath = os.path.join(DATA_DIR, filename)

        data = {
            "id": int(parsed_date.strftime("%Y%m%d")),
            "date": date,
            "day": day_name,
            "text": text,
            "todo": todo
        }

        # Save JSON
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        # Update DB
        entry = db.query(DiaryIndex).filter(DiaryIndex.date == parsed_date).first()
        if not entry:
            entry = DiaryIndex(date=parsed_date, json_path=filepath)
            db.add(entry)

        db.commit()
        return {"message": "Entry saved successfully"}

    finally:
        db.close()

@app.get("/diary/{date}")
def get_entry(date: str):
    file_path = f"{DATA_DIR}/{date}.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Entry not found")

    with open(file_path, "r") as f:
        return json.load(f)


@app.get("/export/txt")
def export_diary():
    files = sorted(os.listdir(DATA_DIR))
    export_path = os.path.join(EXPORT_DIR, "diary_2026.txt")

    with open(export_path, "w") as out:
        for file in files:
            with open(os.path.join(DATA_DIR, file)) as f:
                entry = json.load(f)

            out.write("=" * 45 + "\n")
            out.write(f"Date: {entry['date']} ({entry['day']})\n")
            out.write("=" * 45 + "\n")

            out.write((entry["text"] or "No work") + "\n\n")
            out.write(f"To-Do: {entry['todo'] or 'None'}\n\n")

    return {"message": "Export completed", "file": export_path}
