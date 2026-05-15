from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import List

# Base class
class Base(DeclarativeBase):
    pass


# Parent table (One side)
# class UserNew(Base):
#     __tablename__ = "users_new"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), unique=True)
#     age: Mapped[int] = mapped_column()

metadata = Base.metadata

users = Table(
    "users_new",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("age", Integer),
)

# -------------------------
# Setup & Example Usage
# -------------------------

engine = create_engine("sqlite:///sqlalchemy-fastapi/test.db", echo=False)

Base.metadata.create_all(engine)

# def add_users():
#     u1 = UserNew(name="Aditya01", age=30)
#     u2 = UserNew(name="Aditya02", age=25)
#     u3 = UserNew(name="Aditya03", age=35)
#     with Session(engine) as session:
#         session.add_all([u1, u2, u3])
#         session.commit()

with Session(engine) as session:
    # add_users()
    # stmt = select(UserNew).where(UserNew.age > 18)
    stmt = select(users).where(users.c.age > 18)
    print(stmt.compile(compile_kwargs={"literal_binds": True}))