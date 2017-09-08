# Recognition-and-tracking-robot
    The robot can detect the human face, and identify who the person is, and  through control of the iRobot tracking designated personnel . 
    The robot use dlib to detect and distinguish the face, iRobot as the mobile robot chassis, the size range, the face frame to control the moving chassis. Through the face frame size and position to control the moving chassis. 
    There are four versions of the program according to the progress of the project:
1. first.py：
    This version construct operation interface, click the “Connect” can be connected with iRobot through the serial port, click “Video” can enter the module of face detection and tracking, click the  “Help” can get help instructions, and click “Quit” that you can exit the system.
    This version only can detect the face, and the iRobot is controlled by the size and range of the face frame, when there are many people appear in the camera at the same time, the chassis only tracking the people who on the left side of the video frame.
2. second.py：
    This version adds face recognition module, can identify the people who enter into the video frame, and the shell command line will give the specific names or judgment the stranger. This version can also specify the chassis track a specific object, but due to there are problem of program design, the system is not very stability.
3. third.py：
    This version  store the data from different people separately, according to the number of face which appear in the video frame.  This let the chassis can track stability of the specified person.
4. final-edition.py：
    This version  adds exit mechanism in video capture, and joins the real-time name displayed in video frame. The version also design a double video frame display due to the single recognition is time-consuming and the video will be jammed.
