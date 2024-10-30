from pynput import mouse,keyboard

import time
import pyautogui
import pyperclip
import numpy as np
import cv2
img = pyautogui.screenshot() # x,y,w,h
#cv2.imwrite("./1.jpg",np.array(img))
print(np.array(img))
mouse_ctrl = mouse.Controller()
key_ctrl = keyboard.Controller()
# Read pointer position
print('The current pointer position is {0}'.format(
    mouse_ctrl.position))

# Set pointer position
mouse.position = (10, 20)
print('Now we have moved it to {0}'.format(
    mouse_ctrl.position))

time.sleep(1)

# Move pointer relative to current position
mouse_ctrl.move(5, -5)

# Press and release
mouse_ctrl.press(mouse.Button.left)
mouse_ctrl.release(mouse.Button.left) 

# Double click; this is different from pressing and releasing
# twice on macOS
mouse_ctrl.click(mouse.Button.left, 2)

# Scroll two steps down
mouse_ctrl.scroll(0, 2)


# Press and release space
key_ctrl.press(keyboard.Key.space)
key_ctrl.release(keyboard.Key.space)

# Type a lower case A; this will work even if no key on the
# physical key_ctrl is labelled 'A'
key_ctrl.press('a')
key_ctrl.release('a')

# Type two upper case As
key_ctrl.press('A')
key_ctrl.release('A')
with key_ctrl.pressed(keyboard.Key.shift):
    key_ctrl.press('a')
    key_ctrl.release('a')

# Type 'Hello World' using the shortcut type method
key_ctrl.type('Hello World')


s = "hello world"
s1 = pyperclip.paste()
pyperclip.copy(s)
print(s1)

def on_move(x, y):
    print('Pointer moved to {0}'.format(
        (x, y)))

def on_click(x, y, Button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if not pressed:
        # Stop listener
        return False

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))
    listener.stop()

# Collect events until released
#with mouse.Listener(
#        on_move=on_move,
#        on_click=on_click,
#       on_scroll=on_scroll) as listener:
#    listener.join()

# ...or, in a non-blocking fashion:

listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()

def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
key_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
key_listener.start()

def on_activate_h():
    print('<ctrl>+<alt>+h pressed')

def on_activate_i():
    print('<ctrl>+<alt>+i pressed')

with keyboard.GlobalHotKeys({
        '<ctrl>+<alt>+h': on_activate_h,
        '<ctrl>+<alt>+i': on_activate_i}) as h:
    h.join()