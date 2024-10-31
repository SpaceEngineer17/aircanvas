import os
import cv2
import numpy as np
import tracker.hand as htm
import time
import pygame
pygame.mixer.init()




class Elements:
    def __init__(self):
        self.displayText_start_time = None

    '''
    Add interactive elements to the given frame.

    TODO: 
    1. ADD some functions which gets a pointer/cursor/click/event position
    and perform action based on pointer position.
    2. Manage a list of drawn elements and their properties and add or remove future elements based on them.
      Ex. add new color button with automatic position using priviously drawn element.
    '''
    def addCircleButton(self,frame,pos,color):
        return cv2.circle(frame,pos, 15, color,-1,cv2.LINE_4)

    def roundRectangle(self,src, top_left, bottom_right, radius=1, color=(70,70,70), thickness=1, line_type=cv2.LINE_AA):
        """
        Draws and rounded rectangle.
        """
        #  corners:
        #  p1 - p2
        #  |     |
        #  p4 - p3

        p1 = top_left
        p3 = bottom_right

        p2 = (p3[0],p1[1])
        p4 = (p1[0], p3[1])

        height = abs(bottom_right[0] - top_left[1])

        if radius > 1:
            radius = 1

        corner_radius = int(radius * (height/2))

        if thickness < 0:

            #big rect
            top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
            bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

            top_left_rect_left = (p1[0], p1[1] + corner_radius)
            bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

            top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
            bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

            all_rects = [
            [top_left_main_rect, bottom_right_main_rect], 
            [top_left_rect_left, bottom_right_rect_left], 
            [top_left_rect_right, bottom_right_rect_right]]

            [cv2.rectangle(src, rect[0], rect[1], color, thickness) for rect in all_rects]

        # draw straight lines
        cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
        cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
        cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
        cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

        # draw arcs
        cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, color ,thickness, line_type)
        cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, color , thickness, line_type)
        cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,   color , thickness, line_type)
        cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,  color , thickness, line_type)

        return src
    
    def displayText(frame, text, point, fontFace, fontScale, color, thickness, lineType):
        cv2.putText(frame, text, point, fontFace, fontScale, color, thickness, lineType)

class CanvasWindow:
    """
    self.paintPoints: list
    paintPoints[point] = [(x,y),(b,g,r)]
    -->Therefore point = [position, color]
    """


    def __init__(self,width,height):
        self.canvas = np.zeros((height,width,3)) + 0xFF
        self.CANVAS_WIDTH = width
        self.CANVAS_HEIGHT = height

        self.PAINT_COLOR = 'Yellow'
        self.cleared_paintPoints = None
        self.paintPoints = []
        '''self.paintPointsNone: Contains the indices of 'None' points in self.paintPoints'''
        self.paintPointsNone = [] 

        
        '''-------Trigger variables-----'''
        #Functions: addPointNone(), addPoint()
        #Default value: None by default since len(self.paintPoints) = 0 at __init__
        #Possible values: None, True/paintPoint
        #Must be redefined in call of 'Functions'
        self.last_paintPoint = None


    
    def addPoint(self,point,color):
        """
        Append a new point 'point' in the self.paintPoints list
        with color 'color'.
        Intelligent Function: TODO, if point exists change color
        """
        self.paintPoints.append([point,color])

        #---Trigger variables---
        self.last_paintPoint = True
    
    def addPonitNone(self):
        """
        Append a None point in self.paintPoints as a seperator between two points.
        """
        self.paintPoints.append(None) #None will be the last element, for now
        self.paintPointsNone.append( self.paintPoints.__len__() - 1 ) #Index of last element is len-1

        #---Trigger variables---
        self.last_paintPoint = None

        # print(self.paintPointsNone)
        # print(self.paintPoints)
    
    def undo(self):
        """
        Oh No!? No problem just undo last gesture!
        make a redo next: just store the just now remove points
        """
        #Clear the previous paint
        self.canvas[:, :, :] = 0xFF
        if self.paintPointsNone.__len__() > 1:
            print("ACTION: UNDO")
            self.paintPoints = self.paintPoints[0:self.paintPointsNone[-2]+1 ] # Plus one to include that 'None'
            self.paintPointsNone.pop(-1) # paintPoints will be updated, so update paintPointsNone

            #Save a buffer of remove points for redo
        else:
            if self.cleared_paintPoints!=None:
                self.paintPoints = self.cleared_paintPoints
                self.cleared_paintPoints = None

        # print(self.paintPointsNone)
        # print(self.paintPoints)

    def draw(self,frames=None):
        """
        Draw the paint using paint points.
        If a list:'frames' is passed, then it will be painted with paint points.
        """
        for i in range(1,len(self.paintPoints)):
            if self.paintPoints[i] and self.paintPoints[i-1]:
                cv2.line(self.canvas, self.paintPoints[i-1][0], self.paintPoints[i][0], self.paintPoints[i][1], 5, cv2.LINE_4 )
        
        if frames!=None:
            for frame in frames:
                if type(frame)!=None:
                    for i in range(1,len(self.paintPoints)):
                        if self.paintPoints[i] and self.paintPoints[i-1]:
                            cv2.line(frame, self.paintPoints[i-1][0], self.paintPoints[i][0], self.paintPoints[i][1], 5, cv2.LINE_4 )
        
        #return frames
        #no need to return, since the lists args are referenced
    

    def clear(self):
        print(f"{time.strftime('%Y%m%d_%H:%M:%S')}    ACTION: Clearing Screen")
        if self.cleared_paintPoints==None:
            self.cleared_paintPoints = self.paintPoints
        
        #basically perfrom __init__
        self.PAINT_COLOR = 'Yellow'
        self.paintPoints = []
        self.canvas[:, :, :] = 0xFF

class Music:
    '''
    Creates a virtual instrument with soundfiles in given folder 'path'
    Creates a pygame.mixer.Sound objects with files from the location 'path'
    '''
    def __init__(self,path):
        self.path = path
        self.Sound = pygame.mixer.Sound
        self.keys = {}
    
    def load(self):
        files = os.listdir(self.path)
        files.sort()
        for i in range(len(files)):
            self.keys[i] = self.Sound(os.path.join(self.path, files[i]))

    def play(self,k,maxtime=1000):
        """
        Return the k[ey] that is played!
        """
        if k >= len(self.keys):
            k = k % len(self.keys)
        self.keys[k].play(maxtime=maxtime)
        return k
    

# class Piano(Music):
#     def __init__(self,path):
#         super().__init__(path)

# class Xylophone(Music):
#     def __init__(self, path):
#         super().__init__(path)
    

class Binary:
    def decimal(l):
        '''
        Convert a list of bits to decimal
        bits = [1,0,0,1]
        (1 * 2^3) + (0 * 2^2) + (0 * 2^1) + (1 * 2^0)
        bit : bits[0-->len-1]
        pow : len-1 --> 0
        '''
        length = len(l)
        num = 0
        p = length - 1

        for bit in l:
            num = num + bit * 2**p
            p = p-1
        
        return num
    
    def NOT(l):
        return [int(not i) for i in l]



def save(paint,painter,gestures,trackingCanvas):
    """
    Doesnt seems right here, add outside,
    unless VideoDevice and camera frame are added inside this class
    """
    now = time.strftime("%Y%m%d_%H:%M:%S")
    print(f"{now}    ACTION: Taking Screenshot")
    cv2.imwrite(f'./captures/{now}_paint.jpg',paint,[cv2.IMWRITE_JPEG_QUALITY, 100])
    cv2.imwrite(f'./captures/{now}_painter.jpg',painter,[cv2.IMWRITE_JPEG_QUALITY, 100])
    cv2.imwrite(f'./captures/{now}_gesture.jpg',gestures,[cv2.IMWRITE_JPEG_QUALITY, 100])
    cv2.imwrite(f'./captures/{now}_data.jpg',trackingCanvas,[cv2.IMWRITE_JPEG_QUALITY, 100])



MODES = {
    1:'PAINT',
    2:'MUSIC'
    }
MODE = 1
COLORS = {
    'Pink':(255,0,255),
    'Blue' : (255,0,0),
    'Green': (0,255,0),
    'Red' : (0,0,255),
    'Yellow' :(0,255,255),
    'Black':(20,20,20)
}
WIDTH,HEIGHT = 848,480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
tipIds = [4,8,12,16,20]
detector = htm.HandDetector(detectionCon=0.75)


#----PAINT-----
canvasWindow = CanvasWindow(WIDTH,HEIGHT)
canvasElements = Elements()

clear_canvas_start_time = None
screenshoot_start_time = None
mode_change_start_time = None

#----MUSIC-----
pianoBox = Music("./resources/piano2")
pianoBox.load()
xyloBox = Music("./resources/xylo")
xyloBox.load()


total_time = 0
start_time = time0 = time.time()

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame,1)

    time1 = time.time()
    fps = 1/(time1-time0)
    time0 = time1

    total_time =  time.time() - start_time
    
    #Artificial Intelligence X
    #Machine Learninig X
    #Statistics : Math
    trackCanvas = np.zeros(canvasWindow.canvas.shape) #+ 0xff
    detector.findHands(frame, trackFrames=[trackCanvas])
    hands = detector.findPosition(frame) #frame is used to un-normalize the position coordinates
    phands = detector.getHands(hands) #processed hands only 2 L,R
    totalFingers = 0
    if len(hands) != 0:
        fingers = detector.getFingers(hands)
        #if there are 2 hands, fisrt 5 are left and next are right fingers
        #else if there is one hand then it is hands[0][0]
        fingers = fingers['Left']+fingers['Right']
        totalFingers = fingers.count(1)
    
        # print(fingers)


    """<<<<<<<<<<<<<<-----M O D E S----->>>>>>>>>>>>>>>>>>"""
    if MODE==1:
        """<<<<<<<<<<<<<<-----O P T I O N S----->>>>>>>>>>>>>>>>>>"""
        frame = canvasElements.roundRectangle(frame, (10,110), (70,370), radius=0.7, color=(150,150,150), thickness=2)
        frame = canvasElements.addCircleButton(frame,(40,140),COLORS['Pink'])
        frame = canvasElements.addCircleButton(frame,(40,180),COLORS['Blue'])
        frame = canvasElements.addCircleButton(frame,(40,220),COLORS['Green'])
        frame = canvasElements.addCircleButton(frame,(40,260),COLORS['Red'])
        frame = canvasElements.addCircleButton(frame,(40,300),COLORS['Yellow'])
        frame = canvasElements.addCircleButton(frame,(40,340),COLORS['Black'])

        cv2.putText(trackCanvas, f"MODE: {MODES[MODE]}", (WIDTH-150,20), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)
        cv2.putText(trackCanvas, f"Color: {canvasWindow.PAINT_COLOR}", (WIDTH-150,40), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)


        """<<<<<<<<<<<--------D R A W I N G------->>>>>>>>>>>>>>>>"""
        if len(hands)==1 and totalFingers==1:
            #using only only extended index finger
            finger = hands[0][1][tipIds[fingers.index(1)]]
            center = x,y = finger[1],finger[2]
            cv2.circle(frame, center, 20, (0,255,255), 1, cv2.LINE_4)

            # #TODO: CHECK the position of center over each elements dynamically. Ex: if center in Element.elements do element.action
            # #Optional code, since gestures are added?Keeping this to test dynamic elements implementation.
            # if center[0] <= 70:
            #     if 125 <= center[1] <= 155:
            #         canvasWindow.PAINT_COLOR = 'Black'
            #     elif 165 <= center[1] <= 195:
            #         canvasWindow.PAINT_COLOR = 'Blue'
            #     elif 205 <= center[1] <= 235 :
            #         canvasWindow.PAINT_COLOR = 'Green'
            #     elif 245 <= center[1] <= 275 :
            #         canvasWindow.PAINT_COLOR = 'Red'
            #     elif 285 <= center[1] <= 315 :
            #         canvasWindow.PAINT_COLOR = 'Yellow'
            #     elif 325 <= center[1] <= 355 :
            #         canvasWindow.PAINT_COLOR = 'Grey'
            
            # else:
            canvasWindow.addPoint(center,COLORS[canvasWindow.PAINT_COLOR])
    
        else:
            #Dont connect when stopped/started drawing
            if canvasWindow.last_paintPoint != None:
                canvasWindow.addPonitNone()
            
            """<<<<<<<<------A C T I O N S------>>>>>>>>"""
            if len(hands)==2:
                #Select color (5 0 + ? 1)
                if fingers[0:5]==[0,0,0,0,0]:
                    match totalFingers:
                        case 1: canvasWindow.PAINT_COLOR='Pink'
                        case 2: canvasWindow.PAINT_COLOR='Blue'
                        case 3: canvasWindow.PAINT_COLOR='Green'
                        case 4: canvasWindow.PAINT_COLOR='Red'
                        case 5: canvasWindow.PAINT_COLOR='Yellow'
                        case 0: canvasWindow.PAINT_COLOR='Black'
            
                #Gesture: (5 1 + 0,4 1) clear screen
                elif(fingers[0:5]==[1,1,1,1,1] and fingers[5:10]==[0,1,1,1,1]):
                    if clear_canvas_start_time == None:
                        clear_canvas_start_time = total_time
                    elif 1.95 <= total_time - clear_canvas_start_time <= 2.1:
                        screenshoot_start_time = None
                        canvasWindow.clear()
                    elif total_time - clear_canvas_start_time > 2.15:
                        clear_canvas_start_time = None
            
            elif len(hands)==1:
                #Gesture actions
                if totalFingers == 2:
                    #Gesture Undo
                    if( fingers[1]==1 and  fingers[4]==1 ):
                        canvasWindow.undo()
                    
                    #Gesture: peace (take screenshoot)
                    elif(fingers[1]==1 and fingers[2]==1): 
                        #start timer
                        if screenshoot_start_time==None:
                            screenshoot_start_time = total_time
                        #timer not reached
                        elif total_time - screenshoot_start_time <= 1.8:
                            trackCanvas = canvasElements.roundRectangle(trackCanvas, (100,30), (WIDTH-100,90), radius=0.05, color=(200,200,200), thickness=1)
                            cv2.putText(trackCanvas, f"Taking ScreenShot", (WIDTH//2 - 80,55), cv2.FONT_HERSHEY_PLAIN, 1, COLORS["Red"], 1, cv2.LINE_4)
                            cv2.putText(trackCanvas, f"{int(total_time - screenshoot_start_time)}", (WIDTH//2 - 20,65), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)
                        
                        #perform gesture action and reset trigger variables
                        elif 1.95 <= total_time - screenshoot_start_time <= 2.15:
                            screenshoot_start_time = None

                            #Save finger tip(center) gesture movements, for external use
                            gestures = np.zeros(frame.shape)
                            #c[enter]point,p[aint]color is defined as (x,y), (b,g,r)
                            for i in canvasWindow.paintPoints:
                                if i!=None:
                                    cpoint,pcolor = i
                                    gestures[cpoint[1]][cpoint[0]] = [255,255,255] #BGR format
                            
                            save(canvasWindow.canvas, frame0,gestures,trackCanvas0)
                        #timer passed
                        elif total_time - screenshoot_start_time > 2.15:
                            screenshoot_start_time = None
        
        # frame, trackCanvas = canvasWindow.draw(frames=[frame,trackCanvas])

    elif MODE==2:
        """<<<<<<<<<<<<<<<<<<<-----------------I N T E R F A C E------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>"""
        cv2.putText(trackCanvas, f"MODE: {MODES[MODE]}", (WIDTH-150,20), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)

        """<<<<<<<<<<<<<<<<<<<<<--------------M U S I C------------->>>>>>>>>>>>>>>>>>>>>>>"""
        if hands:
            if len(hands)==2 and (phands['Left'][0] < phands['Right'][0]):
                xyloKey = Binary.decimal(Binary.NOT(fingers[0:6]))
                pianoKey = Binary.decimal(Binary.NOT(fingers[6:10]))

            elif len(hands)==1 and hands[0][0]=='Left':
                xyloKey = Binary.decimal(Binary.NOT(fingers))
                pianoKey=0

            elif len(hands)==1 and hands[0][0]=="Right":
                xyloKey = 0
                pianoKey = Binary.decimal(Binary.NOT(fingers))
            else:
                xyloKey = pianoKey = 0

            if xyloKey!=0:
                xyloKeyPlayed = xyloBox.play(xyloKey)
                cv2.putText(trackCanvas, f"Piano Key: {xyloKeyPlayed}", (WIDTH-150,60), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)

            if pianoKey!=0:
                pianoKeyPlayed = pianoBox.play(pianoKey)
                cv2.putText(trackCanvas, f"Xylo Key: {pianoKeyPlayed}", (WIDTH-150,40), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)
            
            # x % 6(yields 0,1,2,3,4,5) since there are six colors!! 
            canvasWindow.PAINT_COLOR = list(COLORS.keys())[ (xyloKey+pianoKey) % 6] 
            
        


    """>>>>>>>------- G L O B A L   A C T I O N S -------<<<<<<<"""
    if len(hands)==2:
        """SWITCH MODES"""
        if ( phands['Left'][0][1] > phands['Right'][0][1] ):
            # print(fingers)
            #'[0, 1, 0, 0, 1, 0, 1, 0, 0, 1]'  Ignore thumb, ORIENTATION PROBLEM
            #TODO: fps timer seems nice, (is it not??,need proof)
            if fingers[1:5]==[1,0,0,1] and fingers[6:10]==[1,0,0,1]:
                if mode_change_start_time == None:
                    mode_change_start_time = total_time
                elif 1.9 < total_time - mode_change_start_time < 2.2:
                    MODE = 1 if MODE==2 else 2
                    mode_change_start_time = None
                elif total_time - mode_change_start_time > 2.3:
                    mode_change_start_time = None


    #keeping here so to show drawing in music mode
    canvasWindow.draw(frames=[frame,trackCanvas])

    cv2.putText(trackCanvas, f"FPS: {int(fps)}", (WIDTH//2,20), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)
    cv2.putText(trackCanvas, f"Fingers Count: {totalFingers}", (20,20), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)
    cv2.putText(trackCanvas, f"Time: {int(total_time)}", (20,40), cv2.FONT_HERSHEY_PLAIN, 1, COLORS[canvasWindow.PAINT_COLOR], 1, cv2.LINE_4)

    cv2.imshow('Magic Magic!',frame)
    #cv2.imshow("Canvas",canvasWindow.canvas)
    cv2.imshow("Tracking",trackCanvas)
    
    #save frames which gets updated for every while loop
    #how did i referenced instead copying??? dumb fellow
    frame0 = frame.copy()
    trackCanvas0 = trackCanvas.copy()


    if cv2.waitKey(1) == ord('q'):
        break

pygame.mixer.quit()
pygame.quit() 
cap.release()
cv2.destroyAllWindows()
