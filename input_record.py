import time
from psn_controller import BackgroundControllerSingleton



if __name__ == "__main__":
    BackgroundControllerSingleton.wait_start()
    BackgroundControllerSingleton.record()
    while BackgroundControllerSingleton.is_running():
        time.sleep(1)
    print("stop")
    BackgroundControllerSingleton.save_record()