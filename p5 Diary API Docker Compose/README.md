# 📘 Diary API – FastAPI + PostgreSQL (Dockerized)

A backend project to maintain a **daily internship diary** using **FastAPI**, **PostgreSQL**, and **Docker**.
The system stores one entry per day in JSON format and allows exporting the entire diary as a structured text report.

This project is designed to help maintain consistent internship documentation and generate a final report easily.

---

## 🚀 Features

* 📅 One diary entry per day
* 🧾 Stores entries as JSON files
* 🗃️ PostgreSQL for indexing and tracking
* 🐳 Fully Dockerized setup
* 📤 Export full diary as a `.txt` report
* 🧠 Supports missing days (weekends / holidays)
* ⚡ FastAPI with Swagger UI
* 📦 Clean project structure

---

## 🛠 Tech Stack

| Component        | Technology              |
| ---------------- | ----------------------- |
| Backend          | FastAPI                 |
| Database         | PostgreSQL              |
| ORM              | SQLAlchemy              |
| Containerization | Docker & Docker Compose |
| Language         | Python                  |
| API Docs         | Swagger UI              |

---

## 📁 Project Structure

```
p5 Diary API Docker Compose/
│
├── app.py                 # Main FastAPI app
├── database.py            # Database connection
├── models.py              # SQLAlchemy models
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
├── data/                  # Daily JSON diary entries
├── exports/               # Combined diary output
└── README.md
```

---

## ⚙️ Setup & Run Instructions

### 🔹 Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd p5\ Diary\ API\ Docker\ Compose
```

---

### 🔹 Step 2: Start Application

```bash
docker-compose up --build
```

This will:

* Start PostgreSQL
* Start FastAPI server
* Create required folders
* Expose API on port `8000`

---

### 🔹 Step 3: Open API Docs

Open in browser:

```
http://localhost:8000/docs
```

You’ll see Swagger UI with all available endpoints.

---

## 📌 API Usage

### ✅ Create / Update Diary Entry

**POST** `/diary/`

Parameters:

```json
{
  "date": "05-01-2026",
  "text": "Worked on FastAPI backend",
  "todo": "Add export feature"
}
```

✔ Automatically creates JSON file
✔ Updates entry if already exists

---

### ✅ Get Entry by Date

**GET** `/diary/{date}`

Example:

```
/diary/05-01-2026
```

---

### ✅ Export Full Diary

**GET** `/export/txt`

📄 Output:

```
exports/diary_2026.txt
```

Formatted and ready for internship submission.

---

## 🧾 Sample Diary Entry (JSON)

```json
{
  "id": 20260105,
  "date": "05-01-2026",
  "day": "Monday",
  "text": "Worked on backend API development",
  "todo": "Implement export feature"
}
```

---

## 🧠 Use Case

This project is designed to:

* Track daily internship work
* Maintain structured logs
* Generate internship reports easily
* Demonstrate backend + Docker skills
* Serve as a base for future AI/RAG features
