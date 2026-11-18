from database import Base, engine
import models  # noqa: F401  (tables register karne ke liye zaroori)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables created:", ", ".join(Base.metadata.tables))