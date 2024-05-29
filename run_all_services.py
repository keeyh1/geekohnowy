"""This script run all the services at specific port"""
from multiprocessing import Process
import uvicorn


def run_uvicorn_app(app_module: str, host: str, port: int):
    """Run a Uvicorn server for a given app module on the specified host and port."""
    uvicorn.run(app_module, host=host, port=port,
                log_level="info", reload=False)


def start_uvicorn_servers(configs):
    """
    Start multiple Uvicorn servers based on app configurations.
    app_configs is a list of tuples with (app_module, host, port).
    """
    processes = []

    for app_module, host, port in configs:
        process = Process(target=run_uvicorn_app,
                          args=(app_module, host, port))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()  # Wait for all processes to finish


if __name__ == "__main__":
    app_configs = [
        ("waveDataStreamingModule.sample_udp_workflow_module:app", "127.0.0.1", 8010),
        ("waveDataReconstrutionModule.sample_matlab_workflow_module:app", "127.0.0.1", 8011),
        ("waveDataReconstrutionModule.sample_matlab_workflow_module2:app", "127.0.0.1", 8012),
        ("program3Module.sample_matlab_workflow_module:app", "127.0.0.1", 8013),
        ("visualizationModule.jackup_websocket_workflow_module:app", "127.0.0.1", 8014),
        ("visualizationModule.water_websocket_workflow_module:app", "127.0.0.1", 8015),
        # ("stressDataModule.sample_matlab_workflow_module:app", "127.0.0.1", 8013),
    ]
    start_uvicorn_servers(app_configs)
