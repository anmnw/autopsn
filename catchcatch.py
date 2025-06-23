import cv2
from pynput import mouse,keyboard
import time
import os
import pyautogui 
import numpy as np
import cv2
class Catcher():   
    # 写一下按键逻辑：
    # 1 按下~开始新一张图 
    # 2 按下任意ascii键都会新增一个点 点唯一 但是不同按键的权重不一样 1234要严格匹配 qwer可能就是大致的点？ asdf取周围的几个点？
    # 3 按下~保存当前图并且画坐标 生成同名的文件 
    # 4 可能要取保存的图做一个标识的内容？不确定 不管他 
    def on_press(key):
        #if(key == keyboard.Key.esc):
            #BackgroundControllerSingleton.running = True
            
        try:
            if key.char == '`':
                CatcherSington.start_new_img()
            else:
                CatcherSington.save_point(key.char)
            print('alpha numeric key {0} pressed'.format(
                keyboard.Key.char))
        except AttributeError:
            if key == keyboard.Key.esc:
                CatcherSington.running = False
            print('special key {0} pressed'.format(
                key))

    def on_release(key):
        pass
        #print('{0} released'.format(
        #    key))

    def on_move(x, y):
        CatcherSington.x = x
        CatcherSington.y = y
    def save_point(self,key_char):
        self.points[key_char] = [self.x,self.y,
                                 self.img[self.y][self.x][0],
                                 self.img[self.y][self.x][1],
                                 self.img[self.y][self.x][2]]
        print(f"save point {self.points[key_char]}")
    def add_bbox_sample(self):
        print("add bbox_sample")
        bbox = []
        for k,v in self.points.items():
                x,y,r,g,b = v
                if(len(bbox)==0):
                    bbox = [x,y,x,y]
                else:
                    bbox[0] = x if bbox[0]>x else bbox[0]
                    bbox[1] = y if bbox[1]>y else bbox[1]
                    bbox[2] = x if bbox[2]<x else bbox[2]
                    bbox[3] = y if bbox[3]<y else bbox[3]
        #print(bbox)
        if len(bbox)>0:
            x_space = 20 if bbox[2]-bbox[0] < 100 else (bbox[2]-bbox[0])/5
            y_space = 20 if bbox[3]-bbox[1] < 100 else (bbox[3]-bbox[1])/5
            if self.pixel_mode:
                x_space = 1
                y_space = 1
            for y in range(bbox[1],bbox[3],int(y_space)):
                for x in range(bbox[0],bbox[2],int(x_space)):
                    #print(f"{x},{y}")
                    self.points[f"{x}_{y}"] = [x,y,
                                    self.img[y][x][0],
                                    self.img[y][x][1],
                                    self.img[y][x][2]]     
        pass
    def save_map(self,path):
        with open(path, 'w') as file:
            file.write(f"origin_filename = '{path}'\n")
            file.write("point_data={\n")
            for k,v in self.points.items():
                x,y,r,g,b = v
                print(k)
                file.write(f'"{k}":[{x},{y},{r},{g},{b}],\n')
                
            file.write("}")
    
    def save_img(self):
        #timestamp = time.time()
        
        formatted_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
        formatted_time = os.path.join(self.save_path,formatted_time)
        img_rgb = self.img
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB) # 注意一下这里默认形式是rgb的 opencv需要bgr
        cv2.imwrite(formatted_time+".jpg",img_bgr)# 只有保存的时候进行这个转换 默认处理都是用rgb通道逻辑
        for k,v in self.points.items():
            x,y,r,g,b = v

            cv2.putText(img_bgr, str(k), (int(x),int(y)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255-int(r),255-int(g),255-int(b)),thickness=3, lineType=cv2.LINE_AA)
        #    (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2) - 5), cv2.FONT_HERSHEY_SIMPLEX, 4,
        #    _color, thickness=3, lineType=cv2.LINE_AA)
        
        cv2.imwrite(formatted_time+"_mark.jpg",img_bgr) 
        if(self.bbox_mode):
            self.add_bbox_sample()
        self.save_map(formatted_time+".py")
        print("save done:"+formatted_time+"_mark.jpg")
    def start_new_img(self):
        if len(self.points.keys())>0:
            self.save_img()
        img = pyautogui.screenshot() # x,y,w,h

        self.img = np.array(img) # rgb chw
        print(self.img.shape)
        self.points = {}
        #cv2.imwrite("./1.jpg",np.array(img))
    def __init__(self,bbox_mode=False):
        self.save_path = "cfg"
        self.running = True
            # ...or, in a non-blocking fashion:
        self.key_listener = keyboard.Listener(
            on_press=Catcher.on_press,
            on_release=Catcher.on_release)
        self.listener = mouse.Listener(
            on_move=Catcher.on_move )
        self.key_listener.start()
        self.listener.start()
        self.img = np.zeros((100,100,3))
        self.points = {}
        self.x = 0
        self.y = 0
        self.bbox_mode = bbox_mode
        self.pixel_mode = False
        pass

    def is_running(self):
        return self.running
    def wait_start(self):
        while not self.is_running():
            time.sleep(0.1)
    
CatcherSington = Catcher(bbox_mode=False)


if __name__ == "__main__":
    #img = pyautogui.screenshot() # x,y,w,h

    #img = np.array(img) # rgb hwc yx0
    #print(img.shape)
    print("how to use:")
    print("1 push '~' button,start a new photo")
    print("2 click any keyboard key, record mouse position")
    print("3 push '~' again, save all record in folder 'cfg', filename is timestamp")
    while(CatcherSington.is_running()):
        time.sleep(1)
    pass
    print("success")