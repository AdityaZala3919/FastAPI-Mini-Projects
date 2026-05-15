from sqlalchemy import ForeignKey, create_engine, select, union, union_all, literal, desc
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    joinedload,
    selectinload,
)


# =========================
# Base
# =========================
class Base(DeclarativeBase):
    pass

# =========================
# Models
# =========================
class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    salary: Mapped[int]
    phone: Mapped[str]

    
class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    budget: Mapped[int]
    phone: Mapped[str]

# =========================
# Engine
# =========================

engine = create_engine(
    "sqlite:///sqlalchemy-fastapi/test1.db",
    echo=True,  # VERY IMPORTANT
)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

def seed_data(session):
    employees = [
        Employee(
            name="Aditya",
            email="aditya@company.com",
            salary=120000,
            phone="1111111111",
        ),
        Employee(
            name="John",
            email="john@company.com",
            salary=90000,
            phone="2222222222",
        ),
        Employee(
            name="Emma",
            email="emma@company.com",
            salary=150000,
            phone="3333333333",
        ),
        Employee(
            name="Sophia",
            email="sophia@company.com",
            salary=110000,
            phone="4444444444",
        ),
        Employee(
            name="Michael",
            email="michael@company.com",
            salary=130000,
            phone="5555555555",
        ),
    ]

    customers = [
        Customer(
            name="Raj",
            email="raj@gmail.com",
            budget=50000,
            phone="4444444444",
        ),
        Customer(
            name="Sophia",
            email="sophia@gmail.com",
            budget=80000,
            phone="5555555555",
        ),
        Customer(
            name="John",
            email="john_customer@gmail.com",
            budget=70000,
            phone="6666666666",
        ),
        Customer(
            name="Jane",
            email="jane@gmail.com",
            budget=60000,
            phone="7777777777",
        ),
        Customer(
            name="Emily",
            email="emily@gmail.com",
            budget=90000,
            phone="8888888888",
        ),
    ]

    session.add_all(employees)
    session.add_all(customers)

    session.commit()

# =========================
# Seed Data
# =========================
with Session(engine) as session:
    seed_data(session)
    top_employees_subq = (
        select(Employee)
        .order_by(Employee.salary.desc())
        .limit(3)
        .subquery()
    )
    stmt = select(top_employees_subq).where(top_employees_subq.c.name == "Aditya")
    result = session.execute(stmt)
    
    print("\nTop Employees:\n")
    for row in result:
        print(row)