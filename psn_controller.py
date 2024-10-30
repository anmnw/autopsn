from pynput import mouse,keyboard
import time
import cfg_helper
class BackgroundController():
        
    def on_press(key):
        #if(key == keyboard.Key.esc):
            #BackgroundControllerSingleton.running = True
            
        try:
            if key.char == '`':
                BackgroundControllerSingleton.running = not BackgroundControllerSingleton.running
                if(BackgroundControllerSingleton.running == False):
                    BackgroundControllerSingleton.is_ending = True
                    return False
            
            #print('alpha numeric key {0} pressed'.format(
            #    keyboard.Key.char))
        except AttributeError:
            #print('special key {0} pressed'.format(
            #    key))
            pass
    def on_release(key):
        #print('{0} released'.format(
        #    key))
        pass
    def on_press_record(key):
        BackgroundControllerSingleton.record_buffer.append(["key",time.time(),key,0,])
        BackgroundController.on_press(key)
    def on_release_record(key):
        BackgroundControllerSingleton.record_buffer.append(["key",time.time(),key,1])
        BackgroundController.on_release(key)

    def on_move(x, y):
        BackgroundControllerSingleton.record_buffer.append(["mouse",time.time(),x,y])



    def on_click(x, y, Button, pressed):        
        BackgroundControllerSingleton.record_buffer.append(["mouse_key",time.time(),x,y,Button,pressed])


    def on_scroll(x, y, dx, dy):
        pass
    # 开始录像 目前只能录制鼠标左右键 和所有ascii码按键
    def record(self): 
        self.record_buffer = [] 
        self.key_listener.stop()
        self.key_listener = keyboard.Listener(
                on_press=BackgroundController.on_press_record,
                on_release=BackgroundController.on_release_record)
        self.listener = mouse.Listener(
                on_move=BackgroundController.on_move,
                on_click=BackgroundController.on_click,
                on_scroll=BackgroundController.on_scroll)
        self.listener.start()
        self.key_listener.start()
        pass
    def save_record(self,path="tmp_record.py"):
        buffer_head = ["from pynput import mouse,keyboard","import time ","mouse_ctrl = mouse.Controller()","key_ctrl = keyboard.Controller()"]
        buffer = []
        if len(self.record_buffer) == 0:
            return
        
        last_timestamp = self.record_buffer[0][1]
        timestamp = self.record_buffer[0][1]
        for cmd in self.record_buffer:
            last_timestamp = timestamp
            timestamp = cmd[1]
            buffer.append(f"time.sleep({timestamp-last_timestamp})")
            if cmd[0] == "key":
                #press (["key",time.time(),key,0,])
                char_key = 'a'
                key = cmd[2]
                try:
                    char_key = key.char
                    if cmd[3] == 0:
                        s = f"key_ctrl.press('{char_key}')"
                    else:
                        s = f"key_ctrl.release('{char_key}')"
                    buffer.append(s)
                except AttributeError:
                    print('special key {0} pressed'.format(
                        key))
                
            if cmd[0] == "mouse":
                #(["mouse",time.time(),x,y])
                
                buffer.append(f"mouse_ctrl.position = ({cmd[2]}, {cmd[3]})")
                pass
            if cmd[0] == "mouse_key":
                #(["mouse_key",time.time(),x,y,Button,pressed])
                key_char = "mouse.Button.center"
                button = cmd[4]
                if(button== mouse.Button.left):
                    key_char = "mouse.Button.left"
                if(button== mouse.Button.right):
                    key_char = "mouse.Button.right"
                if cmd[5] == True:
                    s = f"mouse_ctrl.press({key_char})"
                else:
                    s = f"mouse_ctrl.release({key_char})"
                buffer.append(f"mouse_ctrl.position = ({cmd[2]}, {cmd[3]})")
                buffer.append(s)
            pass
        with open(path, 'w') as file:
            for item in buffer_head:
                file.write(f"{item}\n")
            for item in buffer:
                file.write(f"{item}\n")
    def enable_record_mouse(self):
        self.record_mouse = True
    def __init__(self):
        self.running = False
        self.record_mouse = False
        self.is_ending = False
            # ...or, in a non-blocking fashion:
        self.key_listener = keyboard.Listener(
            on_press=BackgroundController.on_press,
            on_release=BackgroundController.on_release)
        self.key_listener.start()
        
        
        self.key_ctrl = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()
        self.datas = {"default":[]}
        pass

    def end(self):
        return self.is_ending
    def is_running(self):
        return self.running
    def wait_start(self):
        while not self.is_running():
            time.sleep(0.1)

class PsnController:
    need_output = False
    letter_keys = {
        "l_up":"t",
        "l_down":"g",
        "l_left":"f",
        "l_right":"h",
        "l_stick_up":"w",
        "l_stick_down":"s",
        "l_stick_left":"a",
        "l_stick_right":"d",
        "l_1":"1",
        "l_2":"2",
        "l_3":"3",       
        "r_up":"i",
        "r_down":"k",
        "r_left":"j",
        "r_right":"l",
        "r_stick_up":"[",
        "r_stick_down":"'",
        "r_stick_left":";",
        "r_stick_right":"\\",
        "r_1":"4",
        "r_2":"5",
        "r_3":"6",    
        "option": "x",
        "cross": "k",
        "box": "j",
        "squre": "j",
        "triangle": "i",
        "circle": "l",
        
    }
   
    not_letter_keys = {
        "home":keyboard.Key.esc,
    }
    def press(self,s):
        if( BackgroundControllerSingleton.is_ending):
            print("pause,input command is ",s)
            return 
            pass
        if self.need_output:
            print("input"+s)
        if s in PsnController.letter_keys.keys():
            self.key_ctrl.press(PsnController.letter_keys[s])
            return
        if s in PsnController.not_letter_keys.keys():
            
            if self.need_output:
                print("input not letter"+s)
            self.key_ctrl.press(PsnController.not_letter_keys[s])
            return
        
        #if self.need_output:
        print("psn controler: failed input "+s)
    
    def release(self,s):
        if s in PsnController.letter_keys.keys():
            self.key_ctrl.release(PsnController.letter_keys[s])
            return
        if s in PsnController.not_letter_keys.keys():
            self.key_ctrl.release(PsnController.not_letter_keys[s])
            return
        
        if self.need_output:
            print("psn controler: failed input "+s)
    def move_click(self,x,y,t=0.2):
        
        if( BackgroundControllerSingleton.is_ending):
            print(f"pause,input command is {x} {y}")
            return 
        
        #print("move click")
        self.mouse_ctrl.position=(x,y)
        time.sleep(t)
        self.mouse_ctrl.click(mouse.Button.left, 1)
        pass
    def drag(self,l=[0,0,100,100],t = 2.0,step=10):
        if( BackgroundControllerSingleton.is_ending):
            print(f"pause,input command is {l} ")
            return 
        x1,y1,x2,y2 = l
        tt = t/step
        self.mouse_ctrl.position=(x1,y1)
        time.sleep(tt)
        self.mouse_ctrl.press(mouse.Button.left)
        for i in range(step):
            rate = float(i)/step
            x = x2*rate + x1 *(1.0-rate)
            y = y2*rate + y1 *(1.0-rate)
            self.mouse_ctrl.position=(x,y)
            
            time.sleep(tt)
        
        self.mouse_ctrl.position=(x2,y2)
        time.sleep(tt)
        
        self.mouse_ctrl.release(mouse.Button.left)
    
    def line_click(self,l=[0,0,100,100],t = 2.0,step=10):
        
        if( BackgroundControllerSingleton.is_ending):
            print(f"pause,input command is {l} ")
            return 
        x1,y1,x2,y2 = l
        tt = t/step
        self.mouse_ctrl.position=(x1,y1)
        time.sleep(tt)
        #self.mouse_ctrl.press(mouse.Button.left)
        for i in range(step):
            rate = float(i)/step
            x = x2*rate + x1 *(1.0-rate)
            y = y2*rate + y1 *(1.0-rate)
            self.mouse_ctrl.position=(x,y)
            time.sleep(0.1)
            self.mouse_ctrl.click(mouse.Button.left, 1)

            time.sleep(tt)
            
        
        self.mouse_ctrl.position=(x2,y2)
        time.sleep(tt) 
        self.mouse_ctrl.click(mouse.Button.left, 1)
        #self.mouse_ctrl.release(mouse.Button.left)
    
    def click(self,s,t=0.2):
        self.press(s)
        time.sleep(t)
        self.release(s)
    def go_block(l=[(0,0),(1,1)]):
        ctrl = PsnController()
        start = l[0]
        target = l[1]
        x0 = min(start[0],target[0])
        x1 = max(start[0],target[0])
        y0 = min(start[1],target[1])
        y1 = max(start[1],target[1])
        print(f"go block{x0} {x1} {y0} {y1}")
        for x in range(x0,x1):
            
            time.sleep(0.5)
            if start[0] < target[0]:
                ctrl.click("l_stick_right")
            else :
                ctrl.click("l_stick_left")
        for y in range(y0,y1):
            time.sleep(0.5)
            
            if start[1] < target[1]:
                ctrl.click("l_stick_down")
            else:
                ctrl.click("l_stick_up")
        time.sleep(0.5)
    def __init__(self):
        self.key_ctrl = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()
        pass
    
class GenshinController(PsnController):
    action = {
        "attack" :"r_right",
        "skill2" :"r_up",
        "triangle" :"r_up",
        "skill1" :"r_2",
        "select_object":"r_left",
        "select" :"r_down",
        "cancel" :"r_right",
        "up" :"l_up",
        "down" :"l_down",
        "left" :"l_left",
        "right" :"l_right",
        "move_up" :"l_stick_up",
        "move_down" :"l_stick_down",
        "move_left" :"l_stick_left",
        "move_right" :"l_stick_right",
        "camera_up" :"r_stick_up",
        "camera_down" :"r_stick_down",
        "camera_left" :"r_stick_left",
        "camera_right" :"r_stick_right",
        "option":"option",
        "home":"home",
    }
    def __init__(self):
        
        self.key_ctrl = keyboard.Controller()
        self.mouse_ctrl = mouse.Controller()
        pass
    #def press(self,s):
    #    PsnController.press(self,GenshinController.action[s])
    #def release(self,s):
        
    #    PsnController.release(self,GenshinController.action[s])
    #def click(self,s):
    #    PsnController.click(self,GenshinController.action[s])
    def click_once(self,s):
        s = GenshinController.action[s]
        self.press(s)
        time.sleep(0.1)
        self.release(s)
        pass
    def press_once(self,s):
        s = GenshinController.action[s]
        self.press(s)
    
    def release_once(self,s):
        s = GenshinController.action[s]
        self.release(s)
    




BackgroundControllerSingleton = BackgroundController()

class PointData:
    def __init__(self,s="",d={}):
        self.d = d
        self.psc = PsnController()
        if not s == "":
            self.d = cfg_helper.load_datas("cfg."+s)
    def p(self,s):
        return [self.d[s][0],self.d[s][1]]

    def move_click(self,s,t=0.2):
        x = self.d[s][0]
        y = self.d[s][1]
        print("click",x,y)
        self.psc.move_click(x,y,t)
    def go_block(self,l=["0"],t=[0.5]):
        print(f"go block {l}")
        for i in range(len(l)):
            cmd = l[i]
            tt = t[0]
            self.move_click(cmd)
            if len(t) == len(l):
                tt = t[i]
            time.sleep(tt)
            #print(f"go block {cmd} {tt}")
    
        
if __name__ == "__main__":
    BackgroundControllerSingleton.wait_start()

    ctrl = GenshinController()
    ctrl.click_once("home")
    time.sleep(1)
    ctrl.click_once("up")
    time.sleep(1)
    ctrl.click_once("down")
    time.sleep(1)
    ctrl.click_once("select")
    time.sleep(1)
    ctrl.press_once("left")
    time.sleep(2)
    ctrl.release_once("left")
    time.sleep(2)
    ctrl.click_once("right")
    time.sleep(2)
    ctrl.click_once("right")
    
    time.sleep(2)
    ctrl.click_once("select")
    keyboard.Listener.stop()
    mouse.Listener.stop()