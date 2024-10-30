from catchcatch import CatcherSington
import time

if __name__ == "__main__":
    #img = pyautogui.screenshot() # x,y,w,h

    #img = np.array(img) # rgb hwc yx0
    #print(img.shape)
    CatcherSington.bbox_mode = True
    CatcherSington.pixel_mode = True

    while(CatcherSington.is_running()):
        time.sleep(1)
    pass
    print("success")