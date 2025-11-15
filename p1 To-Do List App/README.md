# FastAPI To-Do List App

A simple To-Do list web application built with FastAPI (Python) for the backend and plain HTML, CSS, and JavaScript for the frontend.
The backend provides RESTful API endpoints to create, read, update, and delete to-do items, while the frontend offers a user-friendly interface to manage tasks.
The app supports task priorities and demonstrates basic CRUD operations with real-time updates.

## Features

- RESTful API for managing to-do items (CRUD)
- Task priorities (High, Medium, Low)
- User-friendly web interface
- Real-time updates after add/delete

## Getting Started

1. **Install dependencies:**
   ```
   pip install fastapi uvicorn
   ```

2. **Run the server:**
   ```
   uvicorn main:api --reload
   ```

3. **Open `http://localhost:8000` in your browser.**

## Project Structure

- `main.py` — FastAPI backend with API endpoints
- `index.html` — Frontend interface

## API Endpoints

- `GET /todos` — List all todos
- `POST /todos` — Add a new todo
- `DELETE /todos/{todo_id}` — Delete a todo
- `PUT /todos/{todo_id}` — Update a todo
