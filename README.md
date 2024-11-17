# aircanvas
A simple python program that can track hands using mediapipe and perform some actions based on fingers count.
It works based on the number of fingers, whether they are closed or open.
Their position can also be used to perform gesture actions.

Module Requirements:
 - Mediapipe
 - Numpy
 - OpenCV
 - PyGame (for playing sounds)

Go to the directory where `magic.py` is.
To run: `python magic.py` <br>
> Tips:
 - 1. The plane of your hand's palm should be parallel to the camera.
   2. Hands should be fully visible in camera frame.
 - [Gestures](/README.md#gestures)
 - [The Program](/README.md#the-program)
 - [Mediapipe Hand Landmarks](/hand-landmarks-mediapipe.png)
 - <b>To change mode</b>: Cross the wrists of left and right hands, and Gesture[0,1,0,0,1, 0,1,0,0,1]

<br><br>
-------
-------
# Gestures

Finger Open = 1 <br>
Finger Closed = 0 <br>
Assume there is a one hand in camera frame. The code will generate a `list` of 5 finger's states. <br>
`[0,1,0,0,0]` This is for Index Finger open. <br>
`[0,0,0,0,0]` This is for all closed fingers.

If there are two hands, the list wiil be `LeftHand + RightHand` <br>
The order of fingers in the list for both hands is `[Thumb, Index, Middle, Ring, Pinky]` <br>
`[1,0,0,0,0, 1,0,0,0,0]` This is Left Thumb Open and Right Thumb Open. <br>
First five elements are Left hand fingers and next are Right.

Some gestures have timer based execution(Clear,Screenshot,ModeChange) and some(Undo) will be executed immediately even if a single frame(very short time period) satisfies the gesture.


# The Program
It has two modes:
 - Painting
 - Music


>Painting
 - One open finger of any hand works as paint brush, drawing stops if there are either more than one fingers open or two hands.
 - Changing Colors : LeftHand[0,0,0,0,0] + RightHand( fingers opened = color number )
 - Undo last drawn line : RightHand[0,1,0,0,1] (Will be executed in the blink of a second)
 - Clear Canvas : Left[1,1,1,1,1] + Right[0,1,1,1,1]
 - Screenshoot : Right[0,1,1,0,0]

>Music
 - LeftHand plays Xylophone and RightHand plays Piano
 - Can use both hands to play at once, unlike Painting
 - Just play in air.
 - The fingers list which is just 0's and 1's will be converted to Decimal value which is then mapped to the corresponding Music Note sound file.
