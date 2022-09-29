from sqlalchemy import create_engine
import sqlalchemy.ext.declarative as decl
import sqlalchemy.orm as orm

SQLALCHEMY_DATABASE_URL = "sqlite:///./sessions.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# connect_args only needed for SQLite3
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
                       "check_same_thread": False})


SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = decl.declarative_base()
