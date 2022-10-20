from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

# internal import. ToDo: We may import declarative-module directly here, if nowere else used.
from database import Base


"""Models for the SQLAchemy ORM go here.

This classes define, how python objects will be translated to rows
in a relational database and vice versa.
"""


class Session(Base):
    """This table holds Session-IDs and their tokens. By returning the right
    token, a user should prove, that he owns an e-mail address.
    """
    __tablename__ = "sessions"

    session = Column(String, primary_key=True, index=True, unique=True)
    host = Column(String, unique=True)
    constituency = Column(Integer)
    confirmed = Column(Boolean) # at least one contact of this session was confirmed


class Contact(Base):
    """Table for holding the E-Mail addresses connected to a Session.
    Every email-address get its own validation token, even if they are
    connected to the same session. So we ensure, that every address must be
    validated separately.
    """
    __tablename__ = "emailAddresses"

    session = Column(String, ForeignKey("sessions.session"), primary_key=True, unique=True)
    email = Column(String, primary_key=True)
    token = Column(String)
    confirmed = Column(Boolean) # only this email was confirmed


class Prefix(Base):
    __tablename__ = "prefixes"

    session = Column(String, ForeignKey("sessions.session"), primary_key=True, index=True, unique=True)
    mesh4 = Column(String, unique=True)
    prefix4 = Column(String, unique=True)
    prefix6 = Column(String, unique=True)
