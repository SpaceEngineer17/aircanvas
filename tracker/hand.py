"""
Hand Tracing Module
By: Murtaza Hassan
Youtube: http://www.youtube.com/c/MurtazasWorkshopRoboticsandAI
Website: https://www.computervision.zone
"""

import cv2
import mediapipe as mp
import time

class HandDetector():
    def __init__(self, static_mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.static_mode = static_mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.static_mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, trackFrames=None):
        """
        Detects hands in an image 'img'.

        Updates the variables:
          self.results [ Used in Funtcion self.findPosition() ]
        Extra Args:
            'frames': list(numpy.array's) : 3 Channel BGR image (conversion will be managed locally)
            Draws landmarks in each frame of frames
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms,self.mpHands.HAND_CONNECTIONS)
            if trackFrames!=None:
                for frame in trackFrames:
                    for handLms in self.results.multi_hand_landmarks:
                        self.mpDraw.draw_landmarks(frame, handLms,self.mpHands.HAND_CONNECTIONS)
    
    def findPosition(self, img):
        """
        Finds the position of all handlandmarks along with their indices.
        Args:   
            img: numpy.array : 3 Channel BGR/RGB/* image.
                 Just for calculating Normalised positions to (x,y) in img.shape
        
        Return dict:
          hands = {
            0: [handLabel, lmList],
            1: [handLabel, lmList],
            2: [handLabel, lmList],
            ..
            ..
            ..
          }
        """
        hands = {}
        if self.results.multi_hand_landmarks:
            for handIndex in range(len(self.results.multi_handedness)):
                handObj = self.results.multi_handedness[handIndex]
                handLabel = handObj.classification[0].label
                lmList = [] #Get the id,position of each biological-points on hands from handObj_landmarks
                for id, lm in enumerate(self.results.multi_hand_landmarks[handIndex].landmark):
                    #print(id, lm)
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # print(id, cx, cy)
                    lmList.append([id, cx, cy])
                
                #Append handIndex and Its data(Left/Right, bio-points) into hands
                hands[handIndex] = [handLabel, lmList]
        
        #Handle mediapipe hands.classification.label and detection error: Note5
        if len(hands)==2:
            HAND_LABEL1 = hands[0][0] #Get the label of first hand( hands[0] )
            HAND_LABEL2 = hands[1][0] #Get the label of second hand( hands[1] )
            if HAND_LABEL1==HAND_LABEL2:
                #changing the type of second hand's classification.label assmuming first hand label is correct
                hands[1][0] = "Left"  if HAND_LABEL1=="Right" else "Right"
        
        return hands
    
    def getHands(self,hands):
        """
        Process 'hands' which is returned from self.findPositions().
        Basically hands.keys() are ignored.
        Arg 'hands':
          hands = {
            0: [handLabel, lmList],
            1: [handLabel, lmList],
          }
          where; handLabel = 'Left'/'Right'

        For now the basic implementation is for 2 hands(Left and Right)
        Return a dict as:
          hands = {
            'Left' : lmList,
            'Right' : lmList
          }
        """
        #Processed hands
        phands = {}
        for hand in hands.values():
            phands[hand[0]] = hand[1]
        
        return phands


    def getFingers(self,hands):
        '''
        Get the fingers open(1)/close(0) from 
        list hands returned from self.findPositions()
        Only works neat for one(L/R) or two hands(L&R).

        Something's Happening here.. Mediapipe Bugs
        '''
        tipIds = [4,8,12,16,20]
        fingers = {'Left':[],'Right':[]}
        
        last_hand = None #Trying to fix mediapipe detection errors
        if hands:
            for i in hands.keys():
                HAND_LABEL = hands[i][0]
                if last_hand==None:
                    last_hand = HAND_LABEL
                elif last_hand==HAND_LABEL:
                    last_hand=None #unnecessary for only two loops.But logical errors should not exists.
                    continue
                lmList = hands[i][1]
                
                """>>>>>>>>>>>>  M A I N   O P E R A T I O N  <<<<<<<<<<<<<"""
                #Special check for thumb
                if HAND_LABEL == 'Right':
                    #palm facing cam
                    if lmList[17][1] >= lmList[5][1]:
                        #open thumb
                        if lmList[4][1] < lmList[3][1]:
                            fingers[HAND_LABEL].append(1)
                        #close thumb
                        else:
                            fingers[HAND_LABEL].append(0)
                    #palm behind cam
                    else:
                        #close thumb
                        if lmList[4][1] < lmList[3][1]:
                            fingers[HAND_LABEL].append(0)
                        #open thumb
                        else:
                            fingers[HAND_LABEL].append(1)
                    
                elif HAND_LABEL == 'Left':
                    #palm facing cam
                    if lmList[17][1] <= lmList[5][1]:
                        #open thumb
                        if lmList[4][1] > lmList[3][1]:
                            fingers[HAND_LABEL].append(1)
                        #close thumb
                        else:
                            fingers[HAND_LABEL].append(0)
                    #palm behind cam
                    else:
                        #close thumb
                        if lmList[4][1] > lmList[3][1]:
                            fingers[HAND_LABEL].append(0)
                        #open thumb
                        else:
                            fingers[HAND_LABEL].append(1)
                
                # 4 Fingers
                for id in range(1, 5):
                    if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                        fingers[HAND_LABEL].append(1)
                    else:
                        fingers[HAND_LABEL].append(0)

        
        return fingers


class Gesture:
    def __init__(self,hands):
        pass
    
    def find(self):
        pass




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

# 1280,720  960,540  848,480  640,360
WIDTH,HEIGHT = 848, 480
#Usage
def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
    detector = HandDetector(maxHands=2)
    while True:
        success, frame = cap.read()
        if not success:
            continue
        frame = cv2.flip(frame, 1)
        detector.findHands(frame)
        BioHands = detector.findPosition(frame)
        fingers = detector.getFingers(BioHands)
        fingers = fingers['Left'] + fingers['Right']

        if len(BioHands) != 0:
            # print(len(BioHands),end=" ::")
            # print(BioHands[0][0],BioHands[1][0] if len(BioHands)==2 else None,end=" ::: ")
            # print(detector.getFingers(BioHands))
            print(decimal(fingers))



        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 255, 255), 3)

        cv2.imshow("Image", frame)
        if cv2.waitKey(1) == ord('q'):
            break


if __name__ == "__main__":
    main()