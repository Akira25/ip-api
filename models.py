from sqlalchemy import Column, Integer, String, Boolean

# internal import. ToDo: We may import declarative-module directly here, if nowere else used.
from database import Base


"""Models for the SQLAchemy ORM go here.

This classes define, how python objects will be translated to rows
in a relational database and vice versa.
"""


class ValidationSession(Base):
    """This table holds Session-IDs and their tokens. By returning the right
    token, a user should prove, that he owns an e-mail address.
    """
    __tablename__ = "openValidations"

    session = Column(String, primary_key=True, index=True, unique=True)
    host = Column(String, unique=True)
    email = Column(String)
    constituency = Column(Integer)
    token = Column(String)
    confirmed = Column(Boolean)


class Session(Base):
    __tablename__ = "sessions"

    session = Column(String, primary_key=True, index=True, unique=True)
    host = Column(String, unique=True)
    email = Column(String)
    constituency = Column(Integer)
    mesh4 = Column(String, unique=True)
    prefix4 = Column(String, unique=True)
    prefix6 = Column(String, unique=True)
    confirmed = Column(Boolean)
