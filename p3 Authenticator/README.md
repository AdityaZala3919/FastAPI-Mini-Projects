# **Authentication API (FastAPI + SQLAlchemy + OAuth2 + JWT)**

A simple authentication backend built using **FastAPI**, **SQLAlchemy ORM**, **OAuth2 Password Flow**, and **JWT (JSON Web Tokens)**.
This API allows users to register, log in, and access protected routes using secure access tokens.

The project demonstrates how to implement authentication from scratch using FastAPI, including password hashing, JWT generation, and dependency-based security handling.

---

## **Features**

* Register new users securely with hashed passwords
* Log in using username and password to receive a JWT access token
* Access protected endpoints using Bearer authentication
* Built-in support for OAuth2 Password Flow with FastAPI’s interactive docs
* Session-management using SQLAlchemy ORM
* Demonstrates dependency injection for authentication and DB sessions
* Clean modular structure with separated models, schemas, security logic, and routes

---

## **Getting Started**

1. **Install dependencies**

   ```bash
   pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart
   ```

2. **Configure your database URL**

   Update this in `database.py`:

   ```python
   SQLALCHEMY_DATABASE_URL = "postgresql://postgres:<password>@localhost:5432/AuthenticatorAPI"
   ```

   *(You can replace PostgreSQL with SQLite if needed.)*

3. **Run the API server**

   ```bash
   uvicorn main:app --reload
   ```

4. Open interactive documentation:

   ```
   http://localhost:8000/docs
   ```

   FastAPI will automatically show the **Authorize** button for OAuth2 token usage.

---

## **Project Structure**

```
AuthAPI/
│── main.py          # FastAPI routes (register, login, protected endpoint)
│── models.py        # SQLAlchemy User model
│── schemas.py       # Pydantic request/response schemas
│── security.py      # JWT creation, password hashing, authentication logic
│── database.py      # DB engine, SessionLocal, Base class
```

---

## **API Endpoints**

### **Authentication**

#### **POST /register**

Register a new user.

**Request example:**

```json
{
  "username": "aditya",
  "email": "aditya@example.com",
  "password": "mypassword"
}
```

---

#### **POST /token**

Log in using username + password to receive a JWT access token.

**Form fields:**

```
username: <your username>
password: <your password>
```

**Response example:**

```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

Use this token inside the Swagger UI "Authorize" button or attach manually as:

```
Authorization: Bearer <token>
```

---

### **Protected Routes**

#### **GET /me**

Fetch details of the currently authenticated user.

*Requires a valid Bearer token.*

---

## **Example Authentication Flow**

1. Register a user via:
   `POST /register`

2. Log in using:
   `POST /token`
   → Receive a JWT token

3. Click **Authorize** in Swagger
   → Enter: `Bearer <your_token>`

4. Access protected routes like:
   `GET /me`
