import socket, io
import traceback
import pyautogui as pg
import pydirectinput as pd

HOST, PORT = ("*.*.*.*", 0000)

pg.FAILSAFE = False
pd.FAILSAFE = False
pd.PAUSE = 0

# 0 - Close connection
# 1 - Key press 0b*******# -> * - key, # - bool
# 2 - Mouse move 5, 2 bytes per x, Y, 1 byte for mouse buttons
# 3 - Screenshot request, quality - 1 byte
HEADERS = {
	1: 1, 
	2: 5, 
	3: 1
}
KM = pd.KEYBOARD_MAPPING
MOUSE = [0, 0]
KEYS = [key for key in KM if KM[key] <= 255]
work = True
host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host.bind((HOST, PORT))

def handle_event(event, data, socket):
	if event == 1:
		key = (data[0] >> 1) & 0b1111111
		pressed = data[0] & 0b1
		pd.keyDown(KEYS[key]) if pressed else pd.keyUp(KEYS[key])
	elif event == 2:
		x = int.from_bytes(data[0:2], "big")
		y = int.from_bytes(data[2:4], "big")
		leftmouse = (data[4]>>1) & 0b1
		rightmouse = data[4] & 0b1
		pd.moveTo(x, y)
		if MOUSE[0] != leftmouse:
			MOUSE[0] = leftmouse
			pd.mouseDown(button="left") if leftmouse else pd.mouseUp(button="left")
		if MOUSE[1] != rightmouse:
			MOUSE[1] = rightmouse
			pd.mouseDown(button="right") if rightmouse else pd.mouseUp(button="right")
	elif event == 3:
		quality = (data[0] >> 1) & 0b1111111
		img_format = bool(data[0] & 0b1)
		img_arr = io.BytesIO()
		if img_format == 0:
			pg.screenshot().save(img_arr, "JPEG", quality=data[0])
		else:
			pg.screenshot().save(img_arr, "PNG")
		img_bytes = img_arr.getvalue()
		length = len(img_bytes).to_bytes(3, "big")
		socket.send(length + img_bytes)

host.listen()
while work:
	socket, _ = host.accept()
	while 1:
		try:
			event = socket.recv(1)
			if not len(event) or event[0] == 0:
				#work = False
				break
			header = HEADERS.get(event[0])
			data = socket.recv(header) if header else b""
			handle_event(event[0], data, socket)
		except Exception as e:
			traceback.print_exc()
host.close()
