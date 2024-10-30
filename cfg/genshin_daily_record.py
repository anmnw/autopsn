from pynput import mouse,keyboard
import time
def main(): 
    mouse_ctrl = mouse.Controller()
    key_ctrl = keyboard.Controller()
    time.sleep(0.0)
    
    key_ctrl.press('f')
    
    time.sleep(0.13398847579956055)
    key_ctrl.release('f')
    time.sleep(0.93398847579956055)
    key_ctrl.press('a')
    time.sleep(0.1781768798828125)
    key_ctrl.release('a')
    time.sleep(1.0031466484069824)
    key_ctrl.press('a')
    time.sleep(0.2559835910797119)
    key_ctrl.release('a')
    time.sleep(0.8045988082885742)
    key_ctrl.press('w')

    time.sleep(2.93398847579956055)
    key_ctrl.release('w') 
    
    time.sleep(0.9647607803344727)
    
    key_ctrl.press('a')
    time.sleep(0.33887505531311035)
    key_ctrl.release('a')
    time.sleep(0.5884280204772949)
    key_ctrl.press('a')
    time.sleep(0.4017300605773926)
    key_ctrl.release('a')
    time.sleep(1.033027172088623)
