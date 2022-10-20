from fastapi import FastAPI, Depends, HTTPException
import sqlalchemy.orm as orm
from ipaddress import IPv4Address, IPv4Network, IPv6Network

from database import SessionLocal, engine
from uuid import uuid4
import json

# from database import *
import crud
import models
import schemas


description = """
This API provides an easy way to register IP-Addresses for the Freifunk Berlin Network automatically.

The process for registering a prefix requires two steps:

1. registering te nodes host-name and the operators contact at the service
2. validating the contact data with the token from the e-mail and thus persisting the prefixes
"""


tags_metadata = [
    {
        "name": "Simple Mode",
        "description": "These operations model address retrieval for a standard standalone falter-router. Most users will use these methods.",
    },
    {
        "name": "Expert Mode",
        "description": "These operations give the possibility to meet special needs. They include i.e. retrieval of one single IPv6-Prefix for a BerlinBackBone site and other special things.",
    },
    {
        "name": "Tools",
        "description": "With the endpoint from tools, you can do useful things which do not fit into simple or expert. For example, there are calls to check for possible IP-Address collisions."
    }
]

app = FastAPI(
    title="Freifunk Berlin – IP-Address API",
    description=description,
    version="0.1.0",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Freifunk Berlin",
        "url": "https://berlin.freifunk.net/",
        "email": "berlin@berlin.freifunk.net",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)

app_id = ""
#db = nipap.NipapApi(app_id)

# development-krams
db_prefixes4 = ["10.36.5.96/27", "10.230.240.192/28",
                "10.31.110.64/28", "10.36.236.128/27"]
db_mesh4 = ["10.31.29.129", "10.31.29.130", "10.31.29.140", "10.31.43.188",
            "10.31.43.189", "10.31.43.190", "10.31.30.117", "10.31.30.118", "10.31.30.119"]
db_prefixes6 = ["2001:bf7:760:400::/56",
                "2001:bf7:800:800::/56", "2001:bf7:820:1900::/56"]


#
# send data in Format for Wizard. Maybe..
#

#
# If prefix didn't get confirmed, router should reset itself...
#

models.Base.metadata.create_all(bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # hier gehts hoch...
        db.close()


@app.post("/api/v1/simplePrefix", tags=["Simple Mode"])
def alloc_simple_prefix(r: schemas.SimplePrefixRequest, db: orm.Session = Depends(get_db)):
    # check, that hostname not already in database
    result = crud.search_hostname(db, r.host)
    if result:
        raise HTTPException(
            422,
            f"The hostname '{r.host}' is already in use!"
        )

    # generate a validation-token and wait for address validation (confirm api call)
    s = models.ValidationSession(
        session=uuid4().hex,
        host=r.host,
        email=r.email,
        constituency=r.constituency,
        token=uuid4.hex(),
        confirmed=False
    )
    crud.create_validation_session(db, s)

    resp = schemas.SimplePrefixResponse(
        session=s.session,
        host=s.host,
        email=s.email,
        constituency=s.constituency,
    )
    return resp

    # alloc the prefixes in nipap
    # try:
    #    mesh = []
    #    mesh.append(db_mesh4.pop())
    #    mesh.append("10.230.240.192")
    #    mesh = json.dumps(mesh)
    #    prefix4_ = db_prefixes4.pop()
    #    prefix6_ = db_prefixes6.pop()
    # except:
    #    raise HTTPException(
    #        500,
    #        "We weren't able to retrieve IP-Addresses for you. They may be all used up. Sorry..."
    #    )

    # save session with prefixes and states in session-database
    # data = models.Session(
    #    session=uuid4().hex,
    #    host=r.host,
    #    email=r.email,
    #    constituency=r.constituency,
    #    mesh4=mesh,
    #    prefix4=prefix4_,
    #    prefix6=prefix6_,
    #    confirmed=False
    # )
    #crud.create_session_data(db, data)

    # send response to client
    #
    # resp = schemas.SimplePrefixResponse(
    #    session=data.session,
    #    host=data.host,
    #    email=data.email,
    #    mesh4=json.loads(data.mesh4),
    #    prefix4=data.prefix4,
    #    prefix6=data.prefix6,
    #    constituency=data.constituency,
    #    constituencyName=schemas.ConstituencyName["c" +
    #                                              str(data.constituency)],
    #    state=schemas.PrefixState.final if data.confirmed == True else schemas.PrefixState.temporary
    # )

    # return resp

# @app.get("/greet/{name}")
# async def greeting(name: str):
#    return f"Hello {name}!"
#


@app.post("api/v1/simplePrefix/confirm", tags=["Simple Mode"])
def validate_token(sessionid: str, token: str, db: orm.Session = Depends(get_db)):
    # validate stuff:
    req = schemas.ConfirmPrefixRequest(
        session=sessionid,
        token=token
    )

    data = crud.read_session_data(db, req.session)

    if not result:
        raise HTTPException(
            422, f"The session '{req.session}' does not exist.")

    s = crud.read_validation_session(db, req.session)
    if s.token != token:
        crud.delete_validation_session(db, req.session)
        raise HTTPException(
            422, "Token was wrong. The server deleted the session. Please start a new request.")

    # alloc prefixes from the prefix database
    try:  # ToDo: substitue with REAL routines
        mesh = []
        mesh.append(db_mesh4.pop())
        mesh.append("10.230.240.192")
        mesh = json.dumps(mesh)
        prefix4_ = db_prefixes4.pop()
        prefix6_ = db_prefixes6.pop()
    except:
        raise HTTPException(
            500,
            "We weren't able to retrieve IP-Addresses for you. They may be all used up. Sorry..."
        )

    # remove validation-data from session-db
    crud.delete_validation_session(db, req.session)

    # send back all the data
    #resp =

    pass


@app.post("/api/v1/simplePrefix/confirm", tags=["Simple Mode"])
def confirm_simple_prefix_allocation(r: schemas.ConfirmPrefixRequest, db: orm.Session = Depends(get_db)):
    # delete temporary flag for the allocation from session-database

    # get prefixes from database
    resp = schemas.ConfirmPrefixResponse(
        session=r.session,
        host=r.host,
        # mesh4=["10.30.50.1"],
        #prefix4: Optional[IPv4Network]
        #prefix6: Optional[IPv6Network]
        state=PrefixState.final
    )

    return resp


# ToDo: Something for deleting the entries made...

@app.post("/api/v1/expertPrefix", tags=["Expert Mode"])
def alloc_expert_prefix(request: schemas.ExpertPrefixRequest):
    pass


@app.post("/api/v1/expertPrefix/confirm", tags=["Expert Mode"])
def confirm_expert_prefix_allocation(request: schemas.ConfirmPrefixRequest):
    pass


@app.post("/api/v1/deletePrefix", tags=["Tools"])
def delete_prefix():
    pass


@app.post("/api/v1/contactMaintainer", tags=["Tools"])
def send_msg_to_Maintainer():
    pass


@app.post("/api/v1/getPrefixesByMail", tags=["Tools"])
def send_prefixes(r: schemas.GetPrefixesByMailRequest):
    pass


@app.get("/api/v1/getPrefixesBySession/{sessionid}", tags=["Tools"])
# Session MUSS validiert sein, um von ihr die Prefixes gelisted zu bekommen!
def list_prefixes():
    pass


# allows automatized addr collision checks
@app.get("/api/v1/addressState/{addr}", tags=["Tools"])
def check_addr_state(addr: IPv4Address):
    pass


@app.get("api/v1/prefix4State/{prefix}", tags=["Tools"])
def check_prefix4_state(prefix: IPv4Network):
    pass


@app.get("api/v1/prefix6State/{prefix}", tags=["Tools"])
def check_prefix4_state(prefix: IPv6Network):
    pass
