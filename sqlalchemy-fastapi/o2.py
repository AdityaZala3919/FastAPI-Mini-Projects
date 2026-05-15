from sqlalchemy import ForeignKey, create_engine, select
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
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user"
    )

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    user: Mapped["User"] = relationship(
        back_populates="posts"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post"
    )

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title})"


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id")
    )

    post: Mapped["Post"] = relationship(
        back_populates="comments"
    )

    def __repr__(self):
        return f"Comment(id={self.id})"


# =========================
# Engine
# =========================

engine = create_engine(
    "sqlite:///sqlalchemy-fastapi/test1.db",
    echo=True,  # VERY IMPORTANT
)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# =========================
# Seed Data
# =========================
with Session(engine) as session:
    users = []
    for user_index in range(1, 4):
        user = User(
            name=f"User {user_index}"
        )
        for post_index in range(1, 4):
            post = Post(
                title=f"Post {post_index} of User {user_index}"
            )
            for comment_index in range(1, 4):
                comment = Comment(
                    content=(
                        f"Comment {comment_index} "
                        f"on Post {post_index}"
                    )
                )
                post.comments.append(comment)
            user.posts.append(post)
        users.append(user)
    session.add_all(users)
    session.commit()

# ==========================================================
# TEST 1 — PURE LAZY LOADING (N+1 PROBLEM)
# ==========================================================
print("\n" + "=" * 50)
print("TEST 1 — LAZY LOADING")
print("=" * 50)

with Session(engine) as session:
    stmt = select(User)
    users = session.scalars(stmt).all()
    for user in users:
        print(f"\nUSER: {user.name}")
        # THIS TRIGGERS QUERY PER USER
        for post in user.posts:
            print(f"  POST: {post.title}")
            # THIS TRIGGERS QUERY PER POST
            for comment in post.comments:
                print(f"    COMMENT: {comment.content}")

# ==========================================================
# TEST 2 — JOINEDLOAD
# ==========================================================
print("\n" + "=" * 50)
print("TEST 2 — JOINEDLOAD")
print("=" * 50)

with Session(engine) as session:
    stmt = (
        select(User)
        .options(
            joinedload(User.posts)
            .joinedload(Post.comments)
        )
    )
    users = session.scalars(stmt).unique().all()
    for user in users:
        print(f"\nUSER: {user.name}")
        for post in user.posts:
            print(f"  POST: {post.title}")
            for comment in post.comments:
                print(f"    COMMENT: {comment.content}")

# ==========================================================
# TEST 3 — SELECTINLOAD
# ==========================================================
print("\n" + "=" * 50)
print("TEST 3 — SELECTINLOAD")
print("=" * 50)

with Session(engine) as session:
    stmt = (
        select(User)
        .options(
            selectinload(User.posts)
            .selectinload(Post.comments)
        )
    )
    users = session.scalars(stmt).all()
    for user in users:
        print(f"\nUSER: {user.name}")
        for post in user.posts:
            print(f"  POST: {post.title}")
            for comment in post.comments:
                print(f"    COMMENT: {comment.content}")