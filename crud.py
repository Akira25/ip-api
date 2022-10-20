import sqlalchemy.orm as orm
from uuid import UUID

import models
import schemas

"""CRUD comes from: Create, Read, Update, and Delete.

So this file defines functions for interacting with data in the session-database
"""


def read_session_data(db: orm.Session, s: UUID):
    return db.query(models.Session).filter(models.Session.session == s).first()


def read_validation_session(db: orm.Session, s: UUID):
    return db.query(models.ValidationSession).filter(models.ValidationSession.session == s).first()

def delete_validation_session(db: orm.Session, s: UUID):
    session = db.query(models.ValidationSession).filter(models.ValidationSession.session == s).first()
    db.delete(session)
    db.commit()
    db.refresh(s)
    return session

def search_hostname(db: orm.Session, hostname: str):
    return db.query(models.Session).filter(models.Session.host == hostname).first()


def create_validation_session(db: orm.Session, s):
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# def create_session_data(db: orm.Session, s: schemas.SessionDBRepresentation):
#    dataset = models.Session(
#        session=s.session,
#        host=s.host,
#        email=s.email,
#        constituency=s.constituency,
#        mesh4=s.mesh4,
#        prefix4=s.prefix4,
#        prefix6=s.prefix6,
#        confirmed=s.confirmed
#    )
#
#    db.add(dataset)
#    db.commit()
#    db.refresh(dataset)
#    return dataset


def update_session_data(db: orm.Session, s: UUID):
    raise NotImplementedError("update_session_data() not implemented yet.")
