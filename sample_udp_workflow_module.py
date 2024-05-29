"""Sample UDP workflow module"""
import asyncio
from collections import deque
from pydantic import BaseModel
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .myLibrary.module_package import (
    ServerStatus, ResponseObject, RESPONSEOBJECTDICT, Status, updateStatus)

origins = ["http://localhost", "http://localhost:8080"]

serverStatus: ServerStatus = {
    "statusList": [],
}

serverVariables = {
    "transport": None,
    "udptask": None,
    "acquire": False,
    "queue": None
}

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load the ML model
#     task = asyncio.create_task(udp_listener(host="127.0.0.1", port=9999))
#     print("Started")
#     yield
#     # Clean up the ML models and release the resources
#     serverVariables["transport"].close()

# Define the FastAPI app
app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/info")
async def info():
    """Return how the api should work"""
    status_param = {
        "input": [],
        "output": "array"
    }
    setup_UDP_param = {
        "input": {
            "ip": "str",
            "port": "int",
            "maxDataSize": "int"
        },
        "output": RESPONSEOBJECTDICT
    }
    start_acquire_param = {
        "input": [],
        "output": RESPONSEOBJECTDICT
    }
    stop_acquire_param = {
        "input": [],
        "output": RESPONSEOBJECTDICT
    }
    clear_data_param = {
        "input": [],
        "output": RESPONSEOBJECTDICT
    }
    get_data_param = {
        "input": [],
        "output": {
            "data": "array"
        }
    }

    return {
        "status": status_param,
        "setup-udp": setup_UDP_param,
        "start-acquire": start_acquire_param,
        "stop-acquire": stop_acquire_param,
        "get-data": get_data_param,
        "clear-data": clear_data_param,
    }


@app.post("/status")
async def status():
    """ Returns the status of the server. """
    return serverStatus


class SetupUDPRequestParam(BaseModel):
    """SetupUDPRequestParam"""
    ip: str
    port: int
    maxDataSize: int


class SetupUDPRequest(BaseModel):
    """SetupUDPRequest"""
    params: SetupUDPRequestParam


@app.post("/setup-udp")
async def setup_udp(request: SetupUDPRequest):
    """ Setup udp connection to visualization"""
    if serverVariables["udptask"] is not None:
        return ResponseObject("setup-udp", Status.ERROR, "UDP server already started").to_dict()
    try:
        serverVariables["udptask"] = asyncio.create_task(
            udp_listener(host=request.params.ip, port=request.params.port))
        serverVariables["queue"] = deque(maxlen=request.params.maxDataSize)
        tmp_response = ResponseObject(
            "setup-udp", Status.READY, "UDP server started")
    except Exception as e:  # pylint: disable=broad-except
        print(f"{e}")
        tmp_response = ResponseObject("setup-udp", Status.ERROR, f"{e}")

    updateStatus(serverStatus["statusList"], tmp_response)
    return tmp_response.to_dict()


@app.post("/start-acquire")
async def start_acquire():
    """Start Acquire"""
    serverVariables["acquire"] = True
    updateStatus(serverStatus["statusList"], ResponseObject(
        "acquire", Status.SUCCESS, "Start acquiring"))
    return ResponseObject("start-acquire", Status.SUCCESS, "Start acquiring")


@app.post("/stop-acquire")
async def stop_acquire():
    """Stop Acquire"""
    serverVariables["acquire"] = False
    updateStatus(serverStatus["statusList"], ResponseObject(
        "acquire", Status.SUCCESS, "Stop acquiring"))
    return ResponseObject("stop-acquire", Status.SUCCESS, "Stop acquiring")


@app.post("/get-data")
async def get_data():
    """Get Data"""
    if serverVariables["queue"] is not None:
        data = np.array(
            list(serverVariables["queue"]), dtype=np.float64).tolist()
        return {"rawWaveData": data}
    else:
        return {"rawWaveData": []}


@app.post("/clear-data")
async def clear_data():
    """Clear Data"""
    if serverVariables["queue"] is not None:
        serverVariables["queue"].clear()
        return ResponseObject("clear-data", Status.SUCCESS, "Clear data")

# class sendDataRequest(BaseModel):
#     data : List[float]

# @app.post("/send")
# async def send(request: sendDataRequest):
#     """Send data to UDP"""
#     if(serverVariables["transport"] is None):
#         return ResponseObject("send",Status.ERROR,"udp is not established").__dict__()
#     try:
#         serverVariables["transport"].sendto(np.array(request.data).tobytes())
#         # ([MyPacketItem(dataType="string",data=""), MyPacketItem(dataType="float",data=[0.1])])
#         tmp_response = ResponseObject("send",Status.SUCCESS,"Data is sent")
#     except Exception as e:  # pylint: disable=broad-except
#         tmp_response = ResponseObject("send",Status.ERROR,f"{e}")

#     updateStatus(serverStatus["statusList"],tmp_response)
#     return tmp_response.to_dict()


async def udp_listener(host: str, port: int):
    """UDP Listener"""
    loop = asyncio.get_running_loop()
    print("Started udp listener")
    transport, _ = await loop.create_datagram_endpoint(
        EchoUDPServerProtocol,
        local_addr=(host, port)
    )
    serverVariables["transport"] = transport


class EchoUDPServerProtocol(asyncio.DatagramProtocol):
    """UDP Server"""

    def connection_made(self, transport):
        self.transport = transport  # pylint: disable=attribute-defined-outside-init

    def datagram_received(self, data, addr): # It inherits the basic structure from asyncio.DatagramProtocol, but the specific behavior is overridden here.
        if (serverVariables["acquire"] and serverVariables["queue"] is not None):
            serverVariables["queue"].append(
                np.frombuffer(data, dtype=np.float64))

    def error_received(self, exc): # It inherits the basic structure from asyncio.DatagramProtocol, but the specific behavior is overridden here.
        updateStatus(serverStatus["statusList"], ResponseObject(
            "udpserver", Status.ERROR, f"{exc}"))
        print(f"Error received: {exc}")

    def connection_lost(self, exc): # It inherits the basic structure from asyncio.DatagramProtocol, but the specific behavior is overridden here.
        updateStatus(serverStatus["statusList"], ResponseObject(
            "udpserver", Status.ERROR, f"Connection closed by peer. {exc}"))
        print("Connection closed by the peer")
