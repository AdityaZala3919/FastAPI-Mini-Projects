from sqlalchemy import Table, Column, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import List


class Base(DeclarativeBase):
    pass


# 🔸 Association table (NO class, just Table)
student_course = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)


# 🔸 Student table
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course,
        back_populates="students"
    )


# 🔸 Course table
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)

    students: Mapped[List["Student"]] = relationship(
        secondary=student_course,
        back_populates="courses"
    )


# -------------------------
# Setup & Usage
# -------------------------

engine = create_engine("sqlite:///test.db", echo=False)
Base.metadata.create_all(engine)

with Session(engine) as session:
    s1 = Student(name="Aditya01")
    s2 = Student(name="Aditya02")

    c1 = Course(title="AI")
    c2 = Course(title="Databases")
    c3 = Course(title="Backend")

    # Link them (this is the magic)
    s1.courses.append(c1)
    s1.courses.append(c3)
    s2.courses.append(c2)
    s2.courses.append(c3)

    session.add_all([s1, s2])
    session.commit()

    # Query
    students = session.query(Student).all()
    for s in students:
        print(s.name, [c.title for c in s.courses])