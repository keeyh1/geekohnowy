import aiohttp
import asyncio
import json
import time

programUrl = "http://127.0.0.1"
portStream = 8010
portRecons = 8011
portRecons2 = 8012
portProgram = 8013
portJack = 8014
portWave = 8015
timeNow = [0, 0]



async def call_get_api(session, api_url, data=None):
    if (data is None):
        async with session.get(f"{api_url}") as response:
            responseJson = await response.json()
            print(f"Response from {api_url}:", responseJson)
            return
    else:
        async with session.get(f"{api_url}", json=data) as response:
            responseJson = await response.json()
            print(f"Response from {api_url}:", responseJson)
            return


async def call_post_api(session, api_url, params=None, data=None):
    if (params is None and data is None):
        async with session.post(f"{api_url}") as response:
            responseJson = await response.json()
            responseStr = f"{responseJson}"
            if len(responseStr) < 300:
                print(f"Response from {api_url}:", responseJson)
            else:
                print(f"Response from {api_url}: some data")
            return responseJson
    else:
        toSend = {"params": params, "data": data}
        async with session.post(f"{api_url}", json=toSend) as response:
            responseJson = await response.json()
            responseStr = f"{responseJson}"
            if len(responseStr) < 300:
                print(f"Response from {api_url}:", responseJson)
            else:
                print(f"Response from {api_url}: some data")
            return responseJson


async def loopJackup(session, dt):
    while True:
        streamResponse = await call_post_api(session, f"{programUrl}:{portStream}/get-data")
        if streamResponse is None:
            print("No data is streaming in")
            await asyncio.sleep(1)
            continue
        aa = time.time()
        reconsResponse = await call_post_api(session, f"{programUrl}:{portRecons2}/run", params={"depth": 6, "fCutMin": 0.05, "fCutMax": 1}, data={"rawWaveData": streamResponse["rawWaveData"]})
        print(f"Jackup Recons Time taken is {time.time()-aa} seconds")
        programResponse = await call_post_api(session, f"{programUrl}:{portProgram}/run", data={"dt": reconsResponse["dt"], "waveHistory": reconsResponse["waveHistory"]})
        await call_post_api(session, f"{programUrl}:{portJack}/update_nodes_and_colors", data={"nodesDisp": programResponse["nodesDisp"], "nodesColor": programResponse["nodesColor"]})
        # await call_post_api(session, f"{programUrl}:{portWave}/update_elevation_and_colors", data={"elevation": reconsResponse["reconsEta"], "nodesColor": reconsResponse["reconsColor"]})
        print(f"Jackup Loop Time taken is {time.time()-timeNow[1]} seconds")
        timeNow[1] = time.time()
        await asyncio.sleep(dt)


async def loopWave(session, dt):
    while True:
        streamResponse = await call_post_api(session, f"{programUrl}:{portStream}/get-data")
        if streamResponse is None:
            print("No data is streaming in")
            await asyncio.sleep(1)
            continue
        print(
            f"Wave Recons first value is {streamResponse['rawWaveData'][0]}, last value is {streamResponse['rawWaveData'][-1]}")
        aa = time.time()
        reconsResponse = await call_post_api(session, f"{programUrl}:{portRecons}/run", params={"depth": 6, "fCutMin": 0.05, "fCutMax": 1}, data={"rawWaveData": streamResponse["rawWaveData"]})
        print(f"Wave Recons Time taken is {time.time()-aa} seconds")
        # programResponse = await call_post_api(session, f"{programUrl}:{portProgram}/run", data={"dt": reconsResponse["dt"], "waveHistory": reconsResponse["waveHistory"]})
        # await call_post_api(session, f"{programUrl}:{portJack}/update_nodes_and_colors", data={"nodesDisp": programResponse["nodesDisp"], "nodesColor": programResponse["nodesColor"]})
        await call_post_api(session, f"{programUrl}:{portWave}/update_elevation_and_colors", data={"elevation": reconsResponse["reconsEta"], "nodesColor": reconsResponse["reconsColor"]})
        print(f"Wave Loop Time taken is {time.time()-timeNow[0]} seconds")
        timeNow[0] = time.time()
        await asyncio.sleep(dt)


async def main():

    async with aiohttp.ClientSession() as session:

        # Wave streaming module
        await call_post_api(session, f"{programUrl}:{portStream}/setup-udp", {"ip": "0.0.0.0", "port": 9999, "maxDataSize": 200})
        await call_post_api(session, f"{programUrl}:{portStream}/start-acquire")

        # Setup recons
        await call_post_api(session, f"{programUrl}:{portRecons}/setup", {"rootFolder": r"C:\Users\zhangs\Desktop\From LYZ\DigitalTwin_20240307\services\waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/connect", {"matlabSessionName": "MATLAB_8280", "rootFolder": r"C:\Users\yunzh\OneDrive\TCOMSwork\002_DigitalTwin\services\waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/setup",{"rootFolder": "/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/connect", {"matlabSessionName": "MATLAB_12992", "rootFolder": r"C:\Users\yunzh\OneDrive\TCOMSwork\002_DigitalTwin\services\waveDataReconstrutionModule"})
        wave_mesh_response = await call_post_api(session, f"{programUrl}:{portRecons}/generate_wave_mesh", {"xmin": -10, "xmax": 10, "dx": 0.1, "ymin": -10, "ymax": 10, "dy": 0.5})

        # Setup recons2
        await call_post_api(session, f"{programUrl}:{portRecons2}/setup", {"rootFolder": r"C:\Users\zhangs\Desktop\From LYZ\DigitalTwin_20240307\services\waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/connect", {"matlabSessionName": "MATLAB_26440", "rootFolder": r"C:\Users\yunzh\OneDrive\TCOMSwork\002_DigitalTwin\services\waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/setup",{"rootFolder": "/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/waveDataReconstrutionModule"})
        # await call_post_api(session, f"{programUrl}:{portRecons}/connect", {"matlabSessionName": "MATLAB_12992", "rootFolder": r"C:\Users\yunzh\OneDrive\TCOMSwork\002_DigitalTwin\services\waveDataReconstrutionModule"})
        _ = await call_post_api(session, f"{programUrl}:{portRecons2}/generate_wave_mesh", {"xmin": -10, "xmax": 10, "dx": 0.1, "ymin": -10, "ymax": 10, "dy": 0.5})

        # Setup Program 3
        await call_post_api(session, f"{programUrl}:{portProgram}/setup", {"rootFolder": r"C:\Users\zhangs\Desktop\From LYZ\DigitalTwin_20240307\services\program3Module"})
        # await call_post_api(session, f"{programUrl}:{portProgram}/connect", {"matlabSessionName": "MATLAB_4540", "rootFolder": r"C:\Users\yunzh\OneDrive\TCOMSwork\002_DigitalTwin\services\program3Module"})
        # await call_post_api(session, f"{programUrl}:{portProgram}/setup",{"rootFolder": "/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/program3Module"})
        # await call_post_api(session, f"{programUrl}:{portProgram}/connect", {"matlabSessionName": "MATLAB_45950", "rootFolder": "/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/program3Module"})
        await call_post_api(session, f"{programUrl}:{portProgram}/read_nodal_dis_modal", {"nodalDisPath": r"C:\Users\zhangs\Desktop\From LYZ\DigitalTwin_20240307\services\program3Module\input\44081\NodalDis_Modal.txt"})

        # Visualization module for Jackup
        await call_post_api(session, f"{programUrl}:{portJack}/setup_websocket", {"ip": "127.0.0.1", "port": 5501, "route": "model"})
        await call_post_api(session, f"{programUrl}:{portJack}/read_file", {"inpFilePath": r"C:\Users\zhangs\Desktop\From LYZ\DigitalTwin_20240307\services\visualizationModule\Basin_EH_Wave_IRRW44071_1.inp"})
        # await call_post_api(session, f"{programUrl}:{portJack}/read_file", {"inpFilePath": r"/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/visualizationModule/Basin_EH_Wave_IRRW44071_1.inp"})
        await call_post_api(session, f"{programUrl}:{portJack}/setup_mesh")

        # Visualization module for Wave
        await call_post_api(session, f"{programUrl}:{portWave}/setup_websocket", {"ip": "127.0.0.1", "port": 5500, "route": "water"})
        # await call_post_api(session, f"{programUrl}:{portJack}/read_file", {"inpFilePath": r"/Users/yunzhi/Library/CloudStorage/OneDrive-Personal/TCOMSwork/002_DigitalTwin/services/visualizationModule/Basin_EH_Wave_IRRW44071_1.inp"})
        await call_post_api(session, f"{programUrl}:{portWave}/setup_mesh", data={"nodes": wave_mesh_response["nodes"], "elems": wave_mesh_response["elems"]})

        # Start for-loop
        dt = 0.01
        await asyncio.gather(
            loopWave(session, dt),
            loopJackup(session, dt)
        )

        # while True:
        #     streamResponse = await call_post_api(session, f"{programUrl}:{portStream}/get-data")
        #     if streamResponse is None:
        #         print("No data is streaming in")
        #         await asyncio.sleep(1)
        #         continue
        #     reconsResponse = await call_post_api(session, f"{programUrl}:{portRecons}/run", params={"depth": 6, "fCutMin": 0.05, "fCutMax": 1}, data={"rawWaveData": streamResponse["rawWaveData"]})
        #     # programResponse = await call_post_api(session, f"{programUrl}:{portProgram}/run", data={"dt": reconsResponse["dt"], "waveHistory": reconsResponse["waveHistory"]})
        #     # await call_post_api(session, f"{programUrl}:{portJack}/update_nodes_and_colors", data={"nodesDisp": programResponse["nodesDisp"], "nodesColor": programResponse["nodesColor"]})
        #     await call_post_api(session, f"{programUrl}:{portWave}/update_elevation_and_colors", data={"elevation": reconsResponse["reconsEta"], "nodesColor": reconsResponse["reconsColor"]})
        #     await asyncio.sleep(dt)


# Execute the main function
if __name__ == "__main__":

    asyncio.run(main())
