from tkinter import *
from PIL import ImageTk, Image
import random
import serial
import time
import struct

SERIAL_PORT = "/dev/tty.Repleo-CH341-003012FD"
MARK_MAX_DELAY = 2
TOUCH_TIMEOUT = 2
RESULT_DISPLAY_TIMEOUT = 0.5

LEFT_ARM = ((1 << 0), 90, 260)
RIGHT_ARM = ((1 << 2), 320, 260)
LEFT_NIPPLE = ((1 << 6), 170, 285)
RIGHT_NIPPLE = ((1 << 7), 240, 285)
LEFT_LEG = ((1 << 5), 150, 480)
RIGHT_LEG = ((1 << 4), 251, 480)
TOUCH_INVALID = (0xFFF5, None, None) #(0xFFFF, None, None)
TOUCHY_POINTS = (LEFT_ARM, RIGHT_ARM, LEFT_NIPPLE, RIGHT_NIPPLE, LEFT_LEG, RIGHT_LEG)

def sync_controller():
    buff = b""
    while b"Hello!\r\n" not in buff:
        buff += controller.read(1)

def flush_controller():
    ptmo = controller.timeout
    controller.timeout = 0.2
    controller.read(1)
    controller.read(controller.in_waiting)
    controller.timeout = ptmo

def is_touched(bit_mask):
    #return state["stage"] == "TOUCH_WAIT"
    while controller.in_waiting >= 2:
        touchy_bits = struct.unpack("<H", controller.read(2))[0]
        touched = bool(touchy_bits & bit_mask)
        if touched:
            return True
    return False

def create_circle(x, y, r, **kwargs):
    canvas.create_oval(x - r, y - r, x + r, y + r, **kwargs)

state = {"stage": "PREPARE", "deadline": 0, "active_touch_point": TOUCH_INVALID, "prev_stage": None}

def update():
    if state["prev_stage"] != state["stage"]:
        print(state["stage"])
        state["prev_stage"] = state["stage"]

    touch_mask, _, _ = state["active_touch_point"]
    if is_touched(touch_mask):
        if state["stage"] == "TOUCH_WAIT":
            state["stage"] = "SUCCESS"
        else:
            state["stage"] = "ERROR"

    if state["stage"] == "PREPARE":
        flush_controller()
        canvas.create_image(0, 0, image = tkimage, anchor = NW)
        state["deadline"] = time.monotonic() + random.uniform(0, MARK_MAX_DELAY)
        state["stage"] = "WAIT_MARK"

    elif state["stage"] == "WAIT_MARK":
        if time.monotonic() > state["deadline"]:
            state["stage"] = "MARK"

    elif state["stage"] == "MARK":
        canvas.create_image(0, 0, image = tkimage, anchor = NW)
        active_touch_point = random.choice(TOUCHY_POINTS)
        state["active_touch_point"] = active_touch_point
        _, x, y = active_touch_point
        create_circle(x, y, r = 10, fill = "blue")
        state["deadline"] = time.monotonic() + TOUCH_TIMEOUT
        state["stage"] = "TOUCH_WAIT"

    elif state["stage"] == "TOUCH_WAIT":
        if time.monotonic() > state["deadline"]:
            state["stage"] = "ERROR"

    elif state["stage"] == "ERROR":
        _, x, y = state["active_touch_point"]
        create_circle(x, y, r = 10, fill = "red")
        state["deadline"] = time.monotonic() + RESULT_DISPLAY_TIMEOUT
        state["stage"] = "SHOW_RESULT"

    elif state["stage"] == "SUCCESS":
        _, x, y = state["active_touch_point"]
        create_circle(x, y, r = 10, fill = "green")
        state["deadline"] = time.monotonic() + RESULT_DISPLAY_TIMEOUT
        state["stage"] = "SHOW_RESULT"

    elif state["stage"] == "SHOW_RESULT":
        if time.monotonic() > state["deadline"]:
            state["stage"] = "PREPARE"

    root.after(50, update)

controller = serial.Serial(SERIAL_PORT, baudrate=115200)
sync_controller()

root = Tk()
image = Image.open("palcika.png")
canvas = Canvas(width = image.width, height = image.height)
canvas.pack(expand = YES, fill = BOTH)
tkimage = ImageTk.PhotoImage(image = image)

update()
mainloop()
