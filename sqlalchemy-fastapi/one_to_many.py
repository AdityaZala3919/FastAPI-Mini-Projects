from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import List

# Base class
class Base(DeclarativeBase):
    pass


# Parent table (One side)
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # One-to-many relationship
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan"
    )


# Child table (Many side)
class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Many-to-one relationship
    author: Mapped["User"] = relationship(back_populates="posts")


# -------------------------
# Setup & Example Usage
# -------------------------

engine = create_engine("sqlite:///sqlalchemy-fastapi/test.db", echo=False)

Base.metadata.create_all(engine)

with Session(engine) as session:
    # Create user
    user = User(name="Aditya2")

    # Create posts
    post1 = Post(title="First Post")
    post2 = Post(title="Second Post")

    # Link posts to user
    user.posts.append(post1)
    user.posts.append(post2)

    session.add(user)
    session.commit()

    # Query
    users = session.query(User).all()
    for u in users:
        print(u.name, [p.title for p in u.posts])