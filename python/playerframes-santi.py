import time
import serial
from os import listdir
from os.path import isfile, join
import random
from datetime import datetime
import pygame
from pygame.locals import *
import time
pygame.init()
WIDTH = 1920
HEIGHT = 1080
TEMPS_RESTART = 6
step = 20  # força del encoder
acceleration = 0.08  # velocitat de rotacio automatica

windowSurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# make sure the 'COM#' is set according the Windows Device Manager
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

counter = 1


def rot_center(image, angle, x, y):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect


def valueChanged(direction, dest, duration):

    if direction == "L":
        dest = dest+step
    elif direction == "R":
        dest = dest-step
    return dest


current_video = 0


def nextVideo(current_video, zoom):
    if zoom:
        name = files[current_video]+"Z"

    else:
        name = files[current_video]
    duration = len(listdir(name+"/"))
    counter=1
    dest=1
    return name, duration, dest


last_stop = time.time()
playing = True
files = ["Allgasog", "Colliemankush", "Garlicbudder", "Hellajelly", "NotoriousTHC", "Nutterbudder", "Poddymouth", "Vanillacreampie"]

pressed = False
zoomed = False
backpressed = False
zoompressed = False
last_static = time.time()
time.sleep(0.1)
dest = 1
name, duration, dest = nextVideo(0, False)
name = "Allgasog"
first = True
while True:

    if time.time() - last_static > TEMPS_RESTART:
        dest += 4

    if(abs(dest-counter) > 15) or first:
        first = False
        counter = (int(counter+(dest-counter)*acceleration))
        img = pygame.image.load(
            name + "/"+str(min(max(1, abs(counter % duration)), duration)).zfill(4)+".jpg")
        img, image_rect = rot_center(img, 90, WIDTH/2, HEIGHT/2)
        image_rect = img.get_rect()
        image_rect.center = windowSurface.get_rect().center
    if ser.in_waiting > 0:
        # read the bytes and convert from binary array to ASCII
        instruccio = ser.readline()

        instruccio = instruccio.decode().strip()

        if instruccio == "B" and not pressed:
            first = True
            if current_video+1 >= len(files):
                current_video = 0
            else:
                current_video += 1
            name, duration, dest = nextVideo(current_video, False)
            counter = 1
            pressed = True

        elif pressed:
            pressed = False

        if instruccio == "P" and not backpressed:
            first = True
            if current_video-1 < 0:
                current_video = len(files)-1
            else:
                current_video -= 1
            name, duration, dest = nextVideo(current_video, False)
            counter = 1
            backpressed = True

        elif backpressed:
            backpressed = False

        if instruccio == "L" or instruccio == "R":
            last_static = time.time()

            dest = valueChanged(instruccio, dest, duration)

        if instruccio == "Z" and not zoomed and not zoompressed:
            first = True
            counter = 1
            dest = 1
            name, duration, dest = nextVideo(current_video, True)
            zoomed = True
            zoompressed = True

        elif instruccio == "Z" and zoomed and not zoompressed:
            first = True
            counter = 1
            dest = 1
            pygame.draw.rect(windowSurface, (0, 0, 0),
                             pygame.Rect(0, 0, WIDTH, HEIGHT))
            name, duration, dest = nextVideo(current_video, False)
            zoomed = False
            zoompressed = True

        if instruccio == "O" and zoompressed:
            zoompressed = False

    events = pygame.event.get()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    windowSurface.fill((0, 0, 0))
    # Replace (0, 0) with desired coordinates
    windowSurface.blit(img, image_rect)
    pygame.display.flip()
    time.sleep(0.02)
