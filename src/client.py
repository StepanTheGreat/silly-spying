import pygame as pg
from PIL import Image
import pydirectinput as pd
import socket, io

KM = pd.KEYBOARD_MAPPING
KEYS = [key for key in KM if KM[key] <= 255]

HOST, PORT = ("*.*.*.*", 0000)
W, H = 1000, 200
FPS = 30
FRAME_RATE = 3
QUALITY = 6; FORMAT = 0

screen = pg.display.set_mode((W, H))
clock = pg.time.Clock()
on_frame_rate = 0
mouse = {"x": 0, "y": 0, "left": 0, "right": 0}

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	socket.connect((HOST, PORT))
except:
	raise SystemExit

def send_key(socket, key, pressed):
	event = bytes([1])
	data = bytes([(key<<1)+pressed])
	socket.send(event+data)

def update_mouse(socket, mouse):
	event = bytes([2])
	x = mouse["x"].to_bytes(2, "big")
	y = mouse["y"].to_bytes(2, "big")
	l, r = mouse["left"]&0b1, mouse["right"]&0b1
	m = bytes([(l<<1)+r])
	data = x+y+m
	socket.send(event+data)

def get_screen(socket, resize=False):
	event = bytes([3])
	data = bytes([(QUALITY<<1)+FORMAT])

	socket.send(event+data)
	head = socket.recv(3)
	length = int.from_bytes(head, "big")
	img_bytes = socket.recv(length)
	while len(img_bytes) != length:
		img_bytes += socket.recv(length-len(img_bytes))
	
	image = Image.open(io.BytesIO(img_bytes))
	surf = pg.image.fromstring(image.tobytes(), image.size, image.mode)
	if resize:
		surf = pg.transform.scale(surf, (W, H))
	return surf

while 1:
	clock.tick(FPS)
	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			socket.close()
			raise SystemExit
		elif event.type == pg.MOUSEMOTION:
			mouse["x"] = event.pos[0]
			mouse["y"] = event.pos[1]
			update_mouse(socket, mouse)
		elif event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
			pressed = 1 if event.type == pg.MOUSEBUTTONDOWN else 0
			if event.button in (1, 3):
				if event.button == 1:
					mouse["left"] = pressed
				elif event.button == 3:
					mouse["right"] = pressed
				update_mouse(socket, mouse)
		elif event.type in (pg.KEYDOWN, pg.KEYUP):
			pressed = 1 if event.type == pg.KEYDOWN else 0
			k = pg.key.name(event.key)
			if k in KEYS:
				send_key(socket, KEYS.index(k), pressed)

	on_frame_rate += 1
	if on_frame_rate >= FRAME_RATE:
		on_frame_rate = 0
		surf = get_screen(socket)
		screen.blit(surf, (0, 0))
		pg.display.update()
