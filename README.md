#Motion Tracking Mount
This project uses the PiCamera and the Pimoroni Pan/Tilt kit.

The project aims to allow a Raspberry Pi with the afformentioned 
hardware to identify moving objects in a video stream and control the 
mount to point to the object. The image capture is done via OpenCV.

Currently, the extent of functionality is controlling the mount through
keyboard "WASD" keys (and "Q" to exit) while the pygame frame is focused,
while also displaying a seperate frame for the video feed.

turret_auto.py has all the functionality of turret_manual.py, but is currently
able to draw rectangles around regions in the frame with sufficient change.
It uses a background-subtraction method, but it is configured to grab the
"reference" frame every n frames.
