from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math




class GameRuntime(object):
    def __init__(self):
        pygame.init()

        self.screen_width = 1920
        self.screen_height = 1080

        self.prev_right_hand_height = 0
        self.prev_left_hand_height = 0
        self.cur_right_hand_height = 0
        self.cur_left_hand_height = 0

        self.gameover = False

        self.pipe_x = self.screen_width
        self.pipe_opening = random.randint(100, self.screen_height)

        self.bird_height = self.screen_height/2
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
        self.frame_surface = pygame.Surface((self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 0, 32)

        # here we will store skeleton data 
        self.bodies = None

    def draw_color_frame(self, frame, target_surface):
        target_surface.lock()
        address = self.kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def run(self):
        # -------- Main Program Loop -----------
        while not self.done:
            # --- Main event loop
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    self.done = True # Flag that we are done so we exit this loop

            # We have a color frame. Fill out back buffer surface with frame's data 
            if self.kinect.has_new_color_frame():
                frame = self.kinect.get_last_color_frame()
                self.draw_color_frame(frame, self.frame_surface)
                frame = None # memory save

            # TODO: Handle body input
            #       Bird/Pipe movement
            #       Collision checking 

            # --- copy back buffer surface pixels to the screen, resize it if needed and keep aspect ratio
            # --- (screen size may be different from Kinect's color frame size) 
            h_to_w = float(self.frame_surface.get_height()) / self.frame_surface.get_width()
            target_height = int(h_to_w * self.screen.get_width())
            surface_to_draw = pygame.transform.scale(self.frame_surface, (self.screen.get_width(), target_height));
            self.screen.blit(surface_to_draw, (0,0))
            surface_to_draw = None # memory save
            pygame.display.update()

            # --- Limit to 60 frames per second
            self.clock.tick(60)

        # Close our Kinect sensor, close the window and quit.
        self.kinect.close()
        pygame.quit()

game = GameRuntime();
game.run();