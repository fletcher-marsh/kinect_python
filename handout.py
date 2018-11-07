from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math
import random



class GameRuntime(object):
    def __init__(self):
        pygame.init()

        self.screenWidth = 1920
        self.screenHeight = 1080

        self.prevRightHandHeight = 0
        self.prevLeftHandHeight = 0
        self.curRightHandHeight = 0
        self.curLeftHandHeight = 0

        self.gameover = False

        self.pipeX = self.screenWidth
        self.pipeOpening = random.randint(100, self.screenHeight)

        self.birdHeight = self.screenHeight/2
        self.flap = 0

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Set the width and height of the window [width/2, height/2]
        self.screen = pygame.display.set_mode((960,540), pygame.HWSURFACE|pygame.DOUBLEBUF, 32)

        # Loop until the user clicks the close button.
        self.done = False

        # Kinect runtime object, we want color and body frames 
        self.kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)

        # back buffer surface for getting Kinect color frames, 32bit color, width and height equal to the Kinect color frame size
        self.frameSurface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None

    def drawBird(self):
        pygame.draw.circle(self.frameSurface, (200, 200, 0),
                           (int(self.screenWidth/2), int(self.screenHeight - self.birdHeight)), 40)

    def drawPipes(self):
        pygame.draw.rect(self.frameSurface, (0, 150, 0),
                        (self.pipeX, 0, 200, self.pipeOpening - 150))
        pygame.draw.rect(self.frameSurface, (0, 150, 0),
                        (self.pipeX, self.pipeOpening + 150, 200, self.screenHeight))

    def collision(self):
        birdX = self.screenWidth / 2
        birdY = self.screenHeight - self.birdHeight

        if ((birdX < self.pipeX + 240 and 
            birdX > self.pipeX - 40) and
            (birdY < self.pipeOpening - 110 or
            birdY > self.pipeOpening + 110)):
            self.gameover = True

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self.done:
            # --- Main event loop
            if self.gameover:
                break
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so we exit this loop

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.drawColorFrame(frame, self.frameSurface)
                frame = None # memory save

            if self.kinect.has_new_body_frame():
                self.bodies = self.kinect.get_last_body_frame()

                if self.bodies is not None:
                    for i in range(self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
                        if not body.is_tracked:
                            continue
                        else:
                            joints = body.joints
                            if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.curLeftHandHeight = joints[PyKinectV2.JointType_HandLeft].Position.y
                            if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                                self.curRightHandHeight = joints[PyKinectV2.JointType_HandRight].Position.y
                self.flap = (self.prevLeftHandHeight - self.curLeftHandHeight) + (self.prevRightHandHeight - self.curRightHandHeight)
                if self.flap < 0:
                    self.flap = 0

                self.prevLeftHandHeight = self.curLeftHandHeight
                self.prevRightHandHeight = self.curRightHandHeight

            #       Bird/Pipe movement
            self.birdHeight -= 5
            self.birdHeight += self.flap * 300
            if self.birdHeight < 0:
                self.birdHeight = 0
            if self.birdHight > self.screenHeight:
                self.screenHeight

            self.pipeX -= 5
            if self.pipeX < 100:
                self.pipeX = self.screenWidth
                self.pipeOpening = random.randint(100, self.screenHeight)

            self.drawBird()
            self.drawPipe()
            #       Collision checking 
            self.collision()
            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            hToW = float(self.frameSurface.get_height()) / self.frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, (self.screen.get_width(), target_height));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None # memory save
            pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

game = GameRuntime();
game.run();
