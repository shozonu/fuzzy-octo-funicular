#Motion Tracking Mount
This project uses the PiCamera and the Pimoroni Pan/Tilt kit.

The project aims to allow a Raspberry Pi with the afformentioned 
hardware to identify moving objects in a video stream and control the 
mount to point to the object. The image capture is done via OpenCV.

Currently, the extent of functionality is controlling the mount through
keyboard "WASD" keys (and "Q" to exit) while the pygame frame is focused,
while also displaying a seperate frame for the video feed.

There is also an issue with the video capture and display not
properly terminating. With this issue being the case, the program needs
to be forcefully killed through commands outside the program.

Currently, this issue is being circumvented by using the waitKey() function
of the video loop to get the keyboard input to break the loop.
