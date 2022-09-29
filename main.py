from fastapi import FastAPI, Depends, HTTPException
from schemas import *
import sqlalchemy
import models
import json
#from database import *
import crud
from database import SessionLocal, engine

#import nipap
# Dev-Krams
from ipaddress import IPv4Address, IPv4Network, IPv6Network

description = """
This API provides an easy way to register IP-Addresses for the Freifunk Berlin Network automatically.

The process for registering a prefix requires two steps:

1. registering te nodes host-name and the operators contact at the service and retrieving the temporary prefixes
2. validating the contact data and persisting the prefixes
"""


tags_metadata = [
    {
        "name": "Simple Mode",
        "description": "These operations model address retrieval for a standard standalone falter-router. Most users will use this methods.",
    },
    {
        "name": "Expert Mode",
        "description": "These operations give the possibility to meet special needs. They include i.e. retrieval of one single IPv6-Prefix for Berlin-backbone site and other special things.",
    },
]

app = FastAPI(
    title="Freifunk Berlin – IP-Address API",
    description=description,
    version="0.1.0",
    #terms_of_service="http://example.com/terms/",
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

"""This class wraps pynipap into an useable API for creating prefixes.
       Before you can use API functions you have to connect to a valid
       nipap instance like the following:

           api_user = 'foo'
           api_pass = 'bar'
           api_host = 'localhost:1337'

           api = Api('nipap-wizard')
           api.connect('http://%s:%s@%s' % (api_user, api_pass, api_host))


       * List all pools
           for p in api.list_all_pools():
               print(p.name)

       * List all prefixes
           for p in api.list_all_prefixes():
               print(p.prefix)

       * Search for free prefixes in a pool:
           api.find_free_prefix('Mesh')
           api.find_free_prefix('Mesh', 26)

       * create prefix from a pool named Mesh
           data = {'customer_id':'foo@bar.de', 'description':'foobar'}
           api.create_prefix_from_pool('Mesh', data = data)

       * create prefix with a specific prefix length from a pool named Mesh
           api.create_prefix_from_pool('Mesh', 26)
    """

# @app.get("/")
# async def root():
#    return {"Hello": "You"}
#
# @app.get("/greet/{name}")
# async def greeting(name: str):
#    return f"Hello {name}!"
#

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
def alloc_simple_prefix(r: SimplePrefixRequest, db: sqlalchemy.orm.Session = Depends(get_db)):
    # check, that hostname not already in database
    result = crud.search_hostname(db, r.host)
    if result:
        raise HTTPException(
            422,
            f"The hostname '{r.host}' is already in use!"
        )

    # alloc the prefixes in nipap
    mesh = [ ]
    mesh.append(db_mesh4.pop())
    mesh.append("10.230.240.192")
    mesh = json.dumps(mesh)
    prefix4_ = db_prefixes4.pop()
    prefix6_ = db_prefixes6.pop()

    # save session with prefixes and states in session-database
    data = models.Session(
        session= uuid4().hex,
        host = r.host,
        email = r.email,
        constituency = r.constituency,
        mesh4 = mesh,
        prefix4 = prefix4_,
        prefix6 = prefix6_,
        confirmed = False
    )
    crud.create_session_data(db, data)

    # send response to client

    resp = SimplePrefixResponse(
        session=data.session,
        host=data.host,
        email=data.email,
        mesh4=json.loads(data.mesh4),
        prefix4=data.prefix4,
        prefix6=data.prefix6,
        constituency=data.constituency,
        constituencyName=ConstituencyName["c" + str(data.constituency)],
        state=PrefixState.final if data.confirmed == True else PrefixState.temporary
    )

    return resp


@app.post("/api/v1/simplePrefix/confirm", tags=["Simple Mode"])
def confirm_simple_prefix_allocation(r: ConfirmPrefixRequest, db: sqlalchemy.orm.session.Session = Depends(get_db)):
    # delete temporary flag for the allocation from session-database

    # get prefixes from database
    resp = ConfirmPrefixResponse(
        session=r.session,
        host=r.host,
        #mesh4=["10.30.50.1"],
        #prefix4: Optional[IPv4Network]
        #prefix6: Optional[IPv6Network]
        state=PrefixState.final
    )

    return resp


# ToDo: Something for deleting the entries made...

@app.post("/api/v1/expertPrefix", tags=["Expert Mode"])
def alloc_expert_prefix(request: ExpertPrefixRequest):
    pass


@app.post("/api/v1/expertPrefix/confirm", tags=["Expert Mode"])
def confirm_expert_prefix_allocation(request: ConfirmPrefixRequest):
    pass
