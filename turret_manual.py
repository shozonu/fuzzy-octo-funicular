import time
import pantilthat
import numpy
import cv2
import pygame
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
from multiprocessing import Process, Pipe

def control(conn):
    #initialize pygame
    pygame.init()
    print("Pygame Initialized")

    #initialize servos
    vAngle = 0.0
    hAngle = 0.0
    pantilthat.servo_one(hAngle)
    pantilthat.servo_two(vAngle)
    speed = 0.2
    print("Servos Initialized")
    
    #using pygame frame to capture keyboard input
    screen = pygame.display.set_mode([480, 480])
    print("Control Process Started")
    while True:
        #update event list
        pygame.event.pump()
        #capture input state in variable
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_q]:
            conn.send(True)
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
            pantilthat.servo_one(hAngle)
        if vertical != 0.0:
            vAngle += vertical
            pantilthat.servo_two(vAngle)

print("Starting __main__")
if __name__ == '__main__':
    # set up pipe object and process
    main_conn, process_conn = Pipe()
    control_process = Process(target = control, args = (process_conn,))
    control_process.start()

    #initialize camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 30
    camera.rotation = 180
    rawCapture = PiRGBArray(camera, size=(640,480))
    time.sleep(0.1)
    print("Camera Initialized")

    # grab the raw NumPy array representing the image
    print("Continuous Video Capture Started")
    for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        image = frame.array

        # show the frame
        cv2.imshow("Video Frame", image)
        key = cv2.waitKey(1)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

	#if signal is recieved from main process, break loop to stop process
        if key == ord('q'):
            print ("Stopping Video Loop")
            break
    control_process.join()
    print("Program Ended Successfully")
