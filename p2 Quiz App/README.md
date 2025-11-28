# **Quiz App API (FastAPI + SQLAlchemy + PostgreSQL)**

A simple Quiz Application backend built using **FastAPI**, **SQLAlchemy ORM**, and **PostgreSQL**.
This API allows you to create quiz questions along with multiple choices and retrieve them using RESTful endpoints.

The project demonstrates how to build relational models, handle nested request data, and perform CRUD operations in a FastAPI-SQLAlchemy setup.

---

## **Features**

* Create quiz questions with multiple choices
* Store and manage data using PostgreSQL + SQLAlchemy
* Retrieve questions and their choices via API endpoints
* Demonstrates FastAPI dependency injection for DB session management
* Proper relational structure: **One Question → Many Choices**

---

## **Getting Started**

1. **Install dependencies**

   ```bash
   pip install fastapi uvicorn sqlalchemy psycopg2
   ```

2. **Configure your PostgreSQL URL**

   Update in `database.py`:

   ```python
   URL_DATABASE = "postgresql://postgres:password@localhost:5432/QuizAppFastAPI"
   ```

3. **Run the API server**

   ```bash
   uvicorn main:app --reload
   ```

4. Open interactive docs:

   ```
   http://localhost:8000/docs
   ```

---

## **Project Structure**

```
QuizAppAPI/
│── main.py        # FastAPI endpoints
│── models.py      # SQLAlchemy models (Questions & Choices)
│── database.py    # DB engine, session, and Base class
```

---

## **API Endpoints**

### **Questions**

* `GET /questions/{question_id}`
  Fetch a question by ID

* `POST /questions/`
  Create a new question with choices
  **Request example:**

  ```json
  {
    "question_text": "What is 2 + 2?",
    "choices": [
      {"choice_txt": "3", "is_correct": false},
      {"choice_txt": "4", "is_correct": true}
    ]
  }
  ```

### **Choices**

* `GET /choices/{question_id}`
  Get all choices for a specific question
