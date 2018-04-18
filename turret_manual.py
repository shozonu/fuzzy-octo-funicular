import time
import pantilthat
from picamera import PiCamera
from picamera.array import PiRGBArray
import pygame
from pygame.locals import *
import cv2
from multiprocessing import Process

#initialize pygame and variables
pygame.init()
global stopVideo
stopVideo = False

#initialize servos
vAngle = 0.0
hAngle = 0.0
pantilthat.servo_one(hAngle)
pantilthat.servo_two(vAngle)
speed = 0.25

print("Finished initialization")

def video():
    #initialize camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(640,480))
    time.sleep(0.1)
    print("Camera Initialized")
    
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    print("Starting Capture")
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
 
        # show the frame
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1)
 
        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        global stopVideo
        if key == ord("q"):
            print("Stopping Video Process")
            break

screen = pygame.display.set_mode([480, 480])
print("Starting __main__")
if __name__ == '__main__':
    video_process = Process(target = video)
    print("Process Target Confirmed")
    video_process.start()
    print("Process Started")
    while True:
        #using pygame for key input
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_q]:
            global stopVideo
            stopVideo = True
            break

        #using integers to determine final servo movement vector
        vertical = 0
        horizontal = 0
        if pressed[pygame.K_w]:
            vertical -= speed
        if pressed[pygame.K_s]:
            vertical += speed
        if pressed[pygame.K_a]:
            horizontal += speed
        if pressed[pygame.K_d]:
            horizontal -= speed

        #max angle enforcement
        if (hAngle + horizontal > 89.0) or (hAngle + horizontal < -89):
            horizontal = 0
        if (vAngle + vertical > 89.0) or (vAngle + vertical < -89):
            vertical = 0

        #step servos
        if horizontal != 0.0:
            hAngle += horizontal
        if vertical != 0.0:
            vAngle += vertical
        pantilthat.servo_one(hAngle)
        pantilthat.servo_two(vAngle)
    print("Control Loop ended")
    video_process.terminate()
