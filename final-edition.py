#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The second edition of the program
from Tkinter import *
import tkMessageBox
import tkSimpleDialog

import struct
import sys, glob  # for listing serial ports
import dlib
import cv2
import os
import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import numpy
import datetime
from skimage import io
#测试
try:
    import serial
except ImportError:
    tkMessageBox.showerror('Import error', 'Please install pyserial.')
    raise

connection = None

TEXTWIDTH = 40  # window width, in characters
TEXTHEIGHT = 16  # window height, in lines

VELOCITYCHANGE = 50
ROTATIONCHANGE = 30

helpText = """\





    \t\t\t\t\t\t\tIIP-Robot\t

    \tDetection And Tracking Robot
    """


class TetheredDriveApp(Tk):
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''
    global j
    j = 0

    def __init__(self):
        Tk.__init__(self)
        self.title("IIP-Robot")
        self.option_add('*tearOff', FALSE)

        self.menubar = Menu()
        self.configure(menu=self.menubar)

        createMenu = Menu(self.menubar, tearoff=False)
        self.menubar.add_command(label="Connect", font=30, command=self.onConnect)
        self.menubar.add_command(label="Video", font=30, command=self.onVideo)
        self.menubar.add_command(label="Help", font=30, command=self.onHelp)
        self.menubar.add_command(label="Quit", font=30, command=self.onQuit)

        self.text = Text(self, height=TEXTHEIGHT, width=TEXTWIDTH, wrap=WORD, font=30)
        self.scroll = Scrollbar(self, command=self.text.yview)
        self.text.configure(font=30, yscrollcommand=self.scroll.set)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll.pack(side=RIGHT, fill=Y)

        self.text.insert(END, helpText)

        # self.bind("<Key>", self.callbackKey)
        # self.bind("<KeyRelease>", self.callbackKey)

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                tkMessageBox.showerror('Not connected!', 'Not connected to a robot!')
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None

        # print ' '.join([str(ord(c)) for c in command])
        # self.text.insert(END, ' '.join([str(ord(c)) for c in command]))
        # self.text.insert(END, '\n')
        # self.text.see(END)

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection

        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print "Lost connection"
            tkMessageBox.showinfo('Uh-oh', "Lost connection to the robot!")
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    def onConnect(self):
        global connection

        if connection is not None:
            tkMessageBox.showinfo('Oops', "You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports))
        except EnvironmentError:
            port = tkSimpleDialog.askstring('Port?', 'Enter COM port to open.')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connected!"
                tkMessageBox.showinfo('Connected', "Connection succeeded!")
            except:
                print "Failed."
                tkMessageBox.showinfo('Failed', "Sorry, couldn't connect to " + str(port))

    def onVideo(self):
        motionChange = False
        predictor_path = "/home/lee/Software/test/shape_predictor_68_face_landmarks.dat"
        face_rec_model_path = "/home/lee/Software/test/dlib_face_recognition_resnet_model_v1.dat"
        faces_folder_path = "/home/lee/Software/pycharm_test/candidate-faces"
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(predictor_path)
        facerec = dlib.face_recognition_model_v1(face_rec_model_path)
        font = ImageFont.truetype("/usr/share/fonts/truetype/华文细黑.TTF", 50)
        descriptors = []

        for f in glob.glob(os.path.join(faces_folder_path, "*.jpg")):
            print("Processing file: {}".format(f))
            img = io.imread(f)
            # win.clear_overlay()
            # win.set_image(img)

            dets = detector(img, 1)
            # print("Number of faces detected: {}".format(len(dets)))

            for k, d in enumerate(dets):
                shape = predictor(img, d)
                # win.clear_overlay()
                # win.add_overlay(d)
                # win.add_overlay(shape)

                face_descriptor = facerec.compute_face_descriptor(img, shape)
                # print ("face_descriptor: {}".format(face_descriptor))

                v = numpy.array(face_descriptor)
                # print ("v: {}".format(v))
                descriptors.append(v)
                # print ("descriptors: {}".format(descriptors))

        win = dlib.image_window()
        cap = cv2.VideoCapture(0)
        c = 1
        time = 10
        label = 0
        while cap.isOpened():

            ret, cv_img = cap.read()
            if cv_img is None:
                break

            ndarray_convert_img = Image.fromarray(cv_img)
            img = cv2.cvtColor(cv_img, cv2.COLOR_RGB2BGR)
            # print label
            if label == 0:
                win.clear_overlay()
                win.set_image(img)
                win.set_title('people')

            cv2.imshow("capture", cv_img)


            dist1 = []
            dist2 = []
            dist3 = []
            str1 = " "
            str2 = " "
            str3 = " "

            # print("Number of faces detected: {}".format(len(dets)))
            # lists = [[0 for k in range(4)] for j in range(10)]
            if (c % time == 0):
                label = 1
                w = 0
                x = 0
                j = 0
                lists = [[0 for i in range(4)] for j in range(10)]
                dets = detector(img, 0)
                self.callbackKeyLeft = False
                self.callbackKeyRight = False
                self.callbackKeyDown = False
                self.callbackKeyUp = False
                # motionChange = True
                candidate = ['张丽梅', '丁高兴', '陈杰', '徐科杰', '李政英',
                             '石光耀', '陈美利', '段宇乐', '李宗辉']
                for k, d in enumerate(dets):
                    lists[k][0] = d.left()
                    lists[k][1] = d.top()
                    lists[k][2] = d.right()
                    lists[k][3] = d.bottom()
                    if w == 0:
                        # starttime = datetime.datetime.now()
                        shape1 = predictor(img, d)
                        face_descriptor1 = facerec.compute_face_descriptor(img, shape1)
                        d_test1 = numpy.array(face_descriptor1)
                        # print ("d_test1: {}".format(d_test1))
                        for i in descriptors:

                            dist_1 = numpy.linalg.norm(i - d_test1)

                            # print ("dist_1: {}".format(dist_1))
                            dist1.append(dist_1)
                            # print ("dist1: {}".format(dist1))

                        c_d1 = dict(zip(candidate, dist1))
                        cd_sorted1 = sorted(c_d1.iteritems(), key=lambda d: d[1])
                        # endtime = datetime.datetime.now()
                        # print (endtime - starttime).microseconds
                        # print ("\ncd_sorted1: {}".format(cd_sorted1))
                    if w == 1:
                        shape2 = predictor(img, d)
                        face_descriptor2 = facerec.compute_face_descriptor(img, shape2)
                        d_test2 = numpy.array(face_descriptor2)

                        for i in descriptors:
                            dist_2 = numpy.linalg.norm(i - d_test2)
                            dist2.append(dist_2)

                        c_d2 = dict(zip(candidate, dist2))
                        cd_sorted2 = sorted(c_d2.iteritems(), key=lambda d: d[1])
                        # print ("\ncd_sorted2: {}".format(cd_sorted2))

                    if w == 2:
                        shape3 = predictor(img, d)
                        face_descriptor3 = facerec.compute_face_descriptor(img, shape3)
                        d_test3 = numpy.array(face_descriptor3)

                        for i in descriptors:
                            dist_3 = numpy.linalg.norm(i - d_test3)
                            dist3.append(dist_3)

                        c_d2 = dict(zip(candidate, dist3))
                        cd_sorted3 = sorted(c_d2.iteritems(), key=lambda d: d[1])
                        # print ("\ncd_sorted3: {}".format(cd_sorted3))
                    w = w + 1
                if len(dets) == 0:
                    self.callbackKeyLeft = False
                    self.callbackKeyRight = False
                    self.callbackKeyDown = False
                    self.callbackKeyUp = False
                    motionChange = True
                    j = 0
                else:
                    if len(dets) == 1:
                        if (((cd_sorted1[1][1] - cd_sorted1[0][1]) < 0.025) or (cd_sorted1[0][1] > 0.44)):
                            # print "\n 这是：陌生人"
                            str1 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这是：", cd_sorted1[0][0]
                            str1 = cd_sorted1[0][0]
                            if (cd_sorted1[0][0] == '李政英'):
                                j = lists[0][3] - lists[0][1]
                                x = lists[0][0]

                        # p = 1
                        # print p
                        print "\n 这是： {}".format(str1)

                    if len(dets) == 2:
                        if (((cd_sorted1[1][1] - cd_sorted1[0][1]) < 0.025) or (cd_sorted1[0][1] > 0.44)):
                            # print "\n 这个人是：陌生人"
                            str1 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这个人是：", cd_sorted1[0][0]
                            str1 = cd_sorted1[0][0]
                            if (cd_sorted1[0][0] == '李政英'):
                                j = lists[0][3] - lists[0][1]
                                x = lists[0][0]

                        if (((cd_sorted2[1][1] - cd_sorted2[0][1]) < 0.025) or (cd_sorted2[0][1] > 0.44)):
                            # print "\n 这个人是：陌生人"
                            str2 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这个人是：", cd_sorted2[0][0]
                            str2 = cd_sorted2[0][0]
                            if (cd_sorted2[0][0] == '李政英'):
                                j = lists[1][3] - lists[1][1]
                                x = lists[1][0]

                        # q = 2
                        # print q
                        print "\n 这是: {} 和 {}".format(str1, str2)
                    if len(dets) == 3:
                        if (((cd_sorted1[1][1] - cd_sorted1[0][1]) < 0.025) or (cd_sorted1[0][1] > 0.44)):
                            # print "\n 这个人是：陌生人"
                            str1 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这个人是：", cd_sorted1[0][0]
                            str1 = cd_sorted1[0][0]
                            if (cd_sorted1[0][0] == '李政英'):
                                j = lists[0][3] - lists[0][1]
                                x = lists[0][0]

                        if (((cd_sorted2[1][1] - cd_sorted2[0][1]) < 0.025) or (cd_sorted2[0][1] > 0.44)):
                            # print "\n 这个人是：陌生人"
                            str2 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这个人是：", cd_sorted2[0][0]
                            str2 = cd_sorted2[0][0]
                            if (cd_sorted2[0][0] == '李政英'):
                                j = lists[1][3] - lists[1][1]
                                x = lists[1][0]

                        if (((cd_sorted3[1][1] - cd_sorted3[0][1]) < 0.025) or (cd_sorted3[0][1] > 0.44)):
                            # print "\n 这个人是：陌生人"
                            str3 = "陌生人"
                            j = 0
                        else:
                            # print "\n 这个人是：", cd_sorted2[0][0]
                            str3 = cd_sorted3[0][0]
                            if (cd_sorted3[0][0] == '李政英'):
                                j = lists[2][3] - lists[2][1]
                                x = lists[2][0]
                        # u = 3
                        # print u
                        print "\n 这是: {} , {} 和 {}".format(str1, str2, str3)


                if x > 300:
                    self.callbackKeyRight = True
                    motionChange = True
                elif 0 < x < 180:
                    self.callbackKeyLeft = True
                    motionChange = True
                elif 180 < x < 300:
                    self.callbackKeyLeft = False
                    self.callbackKeyRight = False
                    motionChange = True
                    if j > 140:
                        self.callbackKeyDown = True
                        motionChange = True
                    elif 0 < j < 110:
                        self.callbackKeyUp = True
                        motionChange = True
                    elif 110 < j < 140:
                        self.callbackKeyDown = False
                        self.callbackKeyUp = False
                        motionChange = True

                if motionChange == True:
                    velocity = 0
                    velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
                    velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
                    rotation = 0
                    rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
                    rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

                    # compute left and right wheel velocities
                    vr = velocity + (rotation / 2)
                    vl = velocity - (rotation / 2)

                    # create drive command
                    cmd = struct.pack(">Bhh", 145, vr, vl)
                    if cmd != self.callbackKeyLastDriveCommand:
                        self.sendCommandRaw(cmd)
                        self.callbackKeyLastDriveCommand = cmd

                draw = ImageDraw.Draw(ndarray_convert_img)
                # draw.text((d.left()-70, d.top()-70), str, (255, 0, 0), font=font)  # 设置文字位置/内容/颜色/字体
                draw.text((lists[0][0]-70, lists[0][1]-70), unicode(str1, 'utf-8'), (255, 0, 0), font=font)
                draw.text((lists[1][0]-70, lists[1][1]-70), unicode(str2, 'utf-8'), (255, 0, 0), font=font)
                draw.text((lists[2][0]-70, lists[2][1]-70), unicode(str3, 'utf-8'), (255, 0, 0), font=font)

                # draw = ImageDraw.Draw(ndarray_convert_img)  # Just draw it!
                img_convert_ndarray = numpy.array(ndarray_convert_img)
                imgee = cv2.cvtColor(img_convert_ndarray, cv2.COLOR_RGB2BGR)
                win.set_image(imgee)
                # self.text.insert(END, win)
                # self.text.insert(END, '\n')
                # self.text.see(END)

                # print ("x: {},  \n  j: {}".format(x,j))

            c = c + 1
            # win.clear_overlay()
            # win.set_image(img)
            # win.add_overlay(dets)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        cap.release()

    def onHelp(self):
        tkMessageBox.showinfo('Help', helpText)

    def onQuit(self):
        if tkMessageBox.askyesno('Really?', 'Are you sure you want to quit?'):
            self.destroy()

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == "__main__":
    app = TetheredDriveApp()
    app.mainloop()
