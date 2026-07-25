from sqlalchemy import text

from app.db.session import engine


def test_connection() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print(result.scalar())


if __name__ == "__main__":
    test_connection()

    