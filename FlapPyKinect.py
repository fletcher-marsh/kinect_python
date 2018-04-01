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

    def collision(self):
        bird_x = int(self.screenWidth/2)
        bird_y = int(self.screenHeight - self.birdHeight)
    
        if ((bird_x < self.pipeX + 240 and 
             bird_x > self.pipeX - 40) and
            (bird_y < self.pipeOpening - 110 or 
             bird_y > self.pipeOpening + 110)):
            self.gameover = True


    def drawBird(self):
        pygame.draw.circle(self.frameSurface, 
                          (200,200,0), 
                          (int(self.screenWidth/2), 
                           int(self.screenHeight - self.birdHeight)), 40)

    def drawPipes(self):
        # top pipe
        pygame.draw.rect(self.frameSurface, 
                        (0, 150, 0), 
                        (self.pipeX, 0, 200, self.pipeOpening - 150))

        # bottom pipe
        pygame.draw.rect(self.frameSurface, 
                        (0, 150, 0), 
                        (self.pipeX, self.pipeOpening + 150, 
                         200, self.screenHeight))

    def drawColorFrame(self, frame, targetSurface):
        targetSurface.lock()
        address = self.kinect.surface_as_array(targetSurface.get_buffer())
        # replacing old frame with new one
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        targetSurface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self.done:
            # --- Main event loop
            if self.gameover:
                font = pygame.font.Font(None, 36)
                text = font.render("Game over!", 1, (0, 0, 0))
                self.frameSurface.blit(text, (100,100))
                break
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so we exit this loop

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.drawColorFrame(frame, self.frameSurface)
                frame = None

            # We have a body frame, so can get skeletons
            if self.kinect.has_new_body_frame(): 
                self.bodies = self.kinect.get_last_body_frame()

                if self.bodies is not None: 
                    for i in range(0, self.kinect.max_body_count):
                        body = self.bodies.bodies[i]
                        if not body.is_tracked: 
                            continue 
                    
                        joints = body.joints 
                        # save the hand positions
                        if joints[PyKinectV2.JointType_HandRight].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curRightHandHeight = joints[PyKinectV2.JointType_HandRight].Position.y
                        if joints[PyKinectV2.JointType_HandLeft].TrackingState != PyKinectV2.TrackingState_NotTracked:
                            self.curLeftHandHeight = joints[PyKinectV2.JointType_HandLeft].Position.y

                        # calculate wing flap
                        self.flap = (self.prevLeftHandHeight - self.curLeftHandHeight) + (self.prevRightHandHeight - self.curRightHandHeight)
                        if math.isnan(self.flap) or self.flap < 0:
                            self.flap = 0

                        # cycle previous and current heights for next time
                        self.prevLeftHandHeight = self.curLeftHandHeight
                        self.prevRightHandHeight = self.curRightHandHeight

            # --- Game logic
            self.birdHeight -= 5
            self.birdHeight += self.flap * 300
            if self.birdHeight <= 0:
                # Don't let the bird fall off the bottom of the screen
                self.birdHeight = 0
            if self.birdHeight >= self.screenHeight:
                # Don't let the bird fly off the top of the screen
                self.birdHeight = self.screenHeight

            # Move the pipes to the left
            self.pipeX -= 5
            # When the pipes are past the bird
            if self.pipeX < 100:
                # Reset the pipes back to the other end of the screen
                self.pipeX = self.screenWidth
                self.pipeOpening = random.randint(100, self.screenHeight)

            # Draw graphics
            self.drawBird()
            self.drawPipes()

            # Collision checking
            self.collision()

            # Optional debugging text
            #font = pygame.font.Font(None, 36)
            #text = font.render(str(self.flap), 1, (0, 0, 0))
            #self.frameSurface.blit(text, (100,100))

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            hToW = float(self.frameSurface.get_height()) / self.frameSurface.get_width()
            targetHeight = int(hToW * self.screen.get_width())
            surfaceToDraw = pygame.transform.scale(self.frameSurface, (self.screen.get_width(), targetHeight));
            self.screen.blit(surfaceToDraw, (0,0))
            surfaceToDraw = None
            pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

game = GameRuntime();
game.run();