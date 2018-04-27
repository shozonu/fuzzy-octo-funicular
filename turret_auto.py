import time
import pantilthat
import numpy
import cv2
import pygame
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
from multiprocessing import Process, Queue

def control(input_q):
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
        if pressed[pygame.K_q] and input_q.empty():
            input_q.put(False)
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

#initialize variables
prevFrame = None
blurAmount = 21
min_area = 500
referenceInterval = 5

sinceReference = referenceInterval - 1

print("Starting __main__")
if __name__ == '__main__':
    # set up pipe object and process
    input_queue = Queue(maxsize = 1)
    control_process = Process(target = control, args = (input_queue,))
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

        numpyFrame = frame.array

        #gray image
        gray = cv2.cvtColor(numpyFrame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (blurAmount, blurAmount), 0)

        #skip rest of this loop's iteration if this was the first frame
        sinceReference += 1
        sinceReference = sinceReference % referenceInterval
        if sinceReference == 0:
            prevFrame = gray
            isFirstFrame = False
            cv2.imshow("Video Frame", numpyFrame)
            cv2.waitKey(1)
            rawCapture.truncate(0)
            continue

        #compute absolute difference between current and previous frame
        frameDelta = cv2.absdiff(prevFrame, gray)
        threshold = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        #dilate frame to fill holes, then find contours
        threshold = cv2.dilate(threshold, None, iterations = 2)
        (contours, _) = cv2.findContours(threshold.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #draw over every valid contour
        for c in contours:
            #ignore if too small
            if cv2.contourArea(c) < min_area:
                continue

            #compute and draw bounding box for each contour in frame
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(numpyFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        

        # show the final image
        cv2.imshow("Video Frame", numpyFrame)
        key = cv2.waitKey(1)

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

	#if signal is recieved from main process, break loop to stop process
        if input_queue.full():
            input_queue.get()
            print ("Stopping Video Loop")
            break
    control_process.join()
    print("Program Ended Successfully")
