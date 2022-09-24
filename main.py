from fastapi import FastAPI
from models import *
#import nipap
# Dev-Krams
from ipaddress import IPv4Address, IPv4Network, IPv6Network

app = FastAPI()

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


@app.post("/api/v1/simplePrefix")
async def alloc_simple_prefix(request: SimplePrefixRequest):

    resp = SimplePrefixResponse(
        session=uuid4(),
        host=request.host,
        email=request.email,
        mesh4=db_mesh4,
        prefix4=db_prefixes4[2],
        prefix6=db_prefixes6[1],
        #constituency=42,
        constituencyName=ConstituencyName.c75,
        state=PrefixState.temporary
    )

    return resp


@app.post("/api/v1/simplePrefix/confirm")
async def finalize_simple_prefix():
    pass


@app.post("/api/v1/expertPrefix")
async def alloc_expert_prefix():
    pass


@app.post("/api/v1/expertPrefix/confirm")
async def finalize_expert_prefix():
    pass
