import sys
import serial
from os import listdir
import os.path 
import random
from datetime import datetime
import pygame
from pygame.locals import *
import time
import argparse
from pathlib import Path

# Sets args
parser = argparse.ArgumentParser(description='Flowertron')
parser.add_argument('--test', action='store_true',
                    help='Sets test mode')
args = parser.parse_args()

# Set constants
FPS = 30
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TYPE = pygame.FULLSCREEN
TEMPS_RESTART = 1
ENCODER_STEP_ANGLE = 5
ENCODER_PAUSE_SECONDS = 5
ACCELERATION = 0.08  # velocitat de rotacio automatica
ROTATION_SPEED = 40 
ROTATION_ACCEL = 50
INFO_OVERLAY_SCREEN_POSITION = 0.3
FILES = ["Allgasog", "Colliemankush", "Garlicbudder", "Hellajelly", "NotoriousTHC", "Nutterbudder", "Poddymouth", "Vanillacreampie"]
VIDEO_PATH = "videos"
AUTO_NEXT_VIDEO_SECONDS = 20
ACTION_SHOW_ROTATE_SEC = 5
ACTION_SHOW_OTHERS_SEC = 4
ACTION_ZOOM_FPS = 2
ACTION_INFO_FPS = 2
ACTION_ROTATE_FPS = 2
ACTION_ROTATE_SEC = 15
ACTION_OTHERS_SEC = 0

# Test mode
if args.test :
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    SCREEN_TYPE = pygame.RESIZABLE

ser = serial.Serial('COM3', 9600, timeout=1)

# Setup pygame
pygame.init()
windowSurface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), SCREEN_TYPE)

def rot_center(image, angle, x, y):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect

def getVideoPath(video_index, zoom) :
    video_name = getVideoName(video_index, zoom)
    return VIDEO_PATH + "/" + video_name

def getVideoName(video_index, zoom) :
    if zoom:
        name = FILES[video_index]+"Z"
    else:
        name = FILES[video_index]
    return name

def getVideoInfoSurface(video_index) :
    path =  Path('./info/'+FILES[video_index]+'.png')   
    if path.is_file() :
        return pygame.image.load(path)
    return None

def getTotalFrames(video_index, zoom) :
    VIDEO_PATH = getVideoPath(video_index, zoom)
    return len(listdir(VIDEO_PATH))

def loadActionFrames(path) :
    frames = []
    for imgname in listdir(path) :
        frame = pygame.image.load(path+'/'+imgname)
        frame = pygame.transform.rotate(frame, 90)
        frame = pygame.transform.scale_by(frame, SCREEN_HEIGHT / 1080 )
        frames.append(frame)
    return frames


def loadFrame(video_index, frame_index, zoom):   
    img_path = getVideoPath(video_index, zoom)+"/"+"{:04d}".format(frame_index+1)+".jpg"
    frame = pygame.image.load(img_path)

    return frame

def toggleInfoOverlay():
    global show_overlay, time_to_next_video, has_user_used_encoder, show_action_rotate, show_actions_other
    time_to_next_video = AUTO_NEXT_VIDEO_SECONDS
    has_user_used_encoder = False
    show_action_rotate = False
    show_actions_other = False
    show_overlay = not show_overlay

def rotateLeftVideo():
    global last_encoder_time, rotation, has_user_used_encoder
    has_user_used_encoder = True
    last_encoder_time = time.time()
    rotation -= ENCODER_STEP_ANGLE

def rotateRightVideo():
    global last_encoder_time, rotation, has_user_used_encoder
    has_user_used_encoder = True
    last_encoder_time = time.time()
    rotation += ENCODER_STEP_ANGLE

def zoomInVideo():
    global cur_zoom, has_user_used_encoder, show_action_rotate, show_actions_other
    has_user_used_encoder = False
    show_action_rotate = False
    show_actions_other = False
    cur_zoom = True

def zoomOutVideo():
    global cur_zoom, has_user_used_encoder, show_action_rotate, show_actions_other
    has_user_used_encoder = False
    show_action_rotate = False
    show_actions_other = False
    cur_zoom = False

def nextVideo():
    global cur_video_index, cur_frame_index, cur_zoom, cur_total_frames, info_overlay, time_to_next_video, show_overlay, rotation, rotation_speed

    cur_video_index = (cur_video_index + 1) % len(FILES)
    cur_frame_index = 0
    cur_zoom = False
    rotation = 0
    rotation_speed = 0
    show_overlay = False
    cur_total_frames = getTotalFrames(cur_video_index, cur_zoom)
    info_overlay = getVideoInfoSurface(cur_video_index)
    info_overlay = pygame.transform.rotate(info_overlay, 90)
    info_overlay = pygame.transform.scale_by(info_overlay, SCREEN_HEIGHT / 1080 )
    time_to_next_video = AUTO_NEXT_VIDEO_SECONDS

    
def prevVideo():
    global cur_video_index, cur_frame_index, cur_zoom, cur_total_frames, info_overlay, time_to_next_video, show_overlay, rotation, rotation_speed

    cur_video_index = (cur_video_index - 1) % len(FILES)
    cur_frame_index = 0
    cur_zoom = False
    rotation = 0
    rotation_speed = 0
    show_overlay = False
    cur_total_frames = getTotalFrames(cur_video_index, cur_zoom)
    info_overlay = getVideoInfoSurface(cur_video_index)
    info_overlay = pygame.transform.rotate(info_overlay, 90)
    info_overlay = pygame.transform.scale_by(info_overlay, SCREEN_HEIGHT / 1080 )
    time_to_next_video = AUTO_NEXT_VIDEO_SECONDS


action_zoom_frames = loadActionFrames('actions/zoom')
action_info_frames = loadActionFrames('actions/info')
action_rotate_frames = loadActionFrames('actions/rotate')
action_rotate_time = 0
has_user_used_encoder = False
show_action_rotate = False
show_actions_other = False

cur_video_index = -1;
nextVideo();


frame = loadFrame(cur_frame_index, cur_video_index, cur_zoom)

prev_frame_index = cur_frame_index
prev_video_index = cur_video_index
prev_zoom = cur_zoom

prev_time = time.time()
total_time = 0
idle_time = 0
delta_time = 0
last_encoder_time = 0
time_to_next_video = AUTO_NEXT_VIDEO_SECONDS

while True:
    # Set frame ticks
    current_time = time.time()
    delta_time = current_time - prev_time
    
    # Limit FPS
    if ((1 / FPS) < delta_time) :    
        total_time += delta_time
        time_to_next_video -= delta_time
        idle_time += delta_time

        # Calc rotation
        if current_time - last_encoder_time > ENCODER_PAUSE_SECONDS :
            rotation_speed = ROTATION_SPEED
            rotation += rotation_speed * delta_time

        # Calc frame index
        cur_frame_index = int(((rotation / 360) * cur_total_frames) % cur_total_frames)

        # Needs to load new frame?
        if prev_frame_index != cur_frame_index or prev_video_index != cur_video_index or prev_zoom != cur_zoom :
            frame = loadFrame(cur_video_index, cur_frame_index, cur_zoom)
            frame = pygame.transform.rotate(frame, 90)
            frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        # Render frame
        windowSurface.fill((0, 0, 0))
        windowSurface.blit(frame, frame.get_rect())

        # Actions
        if not show_action_rotate and not show_actions_other and idle_time > ACTION_ROTATE_SEC :
            show_action_rotate = True

        if has_user_used_encoder and show_action_rotate : 
            action_rotate_time = current_time
            show_action_rotate = False

        if has_user_used_encoder and current_time - action_rotate_time > ACTION_OTHERS_SEC :
            show_actions_other = True

        # Render overlay
        if show_overlay and info_overlay :
            info_overlay_position_x = SCREEN_WIDTH * INFO_OVERLAY_SCREEN_POSITION
            info_overlay_position_y = (SCREEN_HEIGHT - info_overlay.get_rect().height) / 2
            windowSurface.blit(info_overlay, (info_overlay_position_x, info_overlay_position_y))

        # Render zoom action
        if show_actions_other :
            action_zoom_anim = int ( total_time * ACTION_ZOOM_FPS % len(action_zoom_frames))
            action_zoom_frame = action_zoom_frames[action_zoom_anim]
            action_zoom_position_x = SCREEN_WIDTH * 0.88  - action_zoom_frame.get_rect().width
            action_zoom_position_y = SCREEN_HEIGHT - action_zoom_frame.get_rect().height - SCREEN_HEIGHT * 0.1
            windowSurface.blit(action_zoom_frame, (action_zoom_position_x, action_zoom_position_y))

            action_info_anim = int ( total_time * ACTION_INFO_FPS % len(action_info_frames))
            action_info_frame = action_info_frames[action_info_anim]
            action_info_position_x = SCREEN_WIDTH * 0.88  - action_info_frame.get_rect().width
            action_info_position_y = SCREEN_HEIGHT * 0.1
            windowSurface.blit(action_info_frame, (action_info_position_x, action_info_position_y))

        # Render rotate action
        if show_action_rotate :
            action_rotate_anim = int ( total_time * ACTION_ROTATE_FPS % len(action_rotate_frames))
            action_rotate_frame = action_rotate_frames[action_rotate_anim]
            action_rotate_position_x = SCREEN_WIDTH / 2  - action_rotate_frame.get_rect().width / 2
            action_rotate_position_y = SCREEN_HEIGHT / 2  - action_rotate_frame.get_rect().height / 2
            windowSurface.blit(action_rotate_frame, (action_rotate_position_x, action_rotate_position_y))

        pygame.display.flip()    

        # Store previous state
        prev_frame_index = cur_frame_index
        prev_video_index = cur_video_index
        prev_zoom = cur_zoom

        # Handle serial inputs
        if ser.in_waiting > 0:
            action = ser.read()
            action = action.decode().strip().upper()
            idle_time = 0
            if not show_overlay :
                time_to_next_video = AUTO_NEXT_VIDEO_SECONDS

            # Zoom in
            if action == "Z":
                zoomInVideo()

            # Zoom out
            elif action == "O":
                zoomOutVideo()

            # Prev video
            if action == "B":
                prevVideo()

            # Next video
            elif action == "P":
                nextVideo()
            
            # Next video
            if action == "I":
                toggleInfoOverlay()

            if action == "L" or action == "R":
                if action == "L" :
                    rotateLeftVideo()
                else :
                    rotateRightVideo()
        
        events = pygame.event.get()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        if time_to_next_video < 0 :
            nextVideo()
                
        prev_time = current_time    
