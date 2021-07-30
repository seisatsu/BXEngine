#####################
# BXEngine          #
# app.py            #
# Copyright 2021    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

import pygame
import pygame_gui

from lib.cursor import Cursor
from lib.logger import Logger


class App(object):
    """
    A class to manage our event, game loop, and overall program flow.
    """

    def __init__(self, config, images, world, gui, resource):
        """
        Get a reference to the screen (created in main); define necessary attributes.
        """
        self.screen = pygame.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pygame.key.get_pressed()
        self.cursor = Cursor()
        self.config = config
        self.images = images
        self.world = world
        self.gui = gui
        self.resource = resource
        self.text_dialog = None
        self.vars = {}
        self.logger = Logger("App")

    def event_loop(self):
        """
        This is the event loop for the whole program.
        We handle clicks and navigation and cleaning up UI elements here.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or self.keys[pygame.K_ESCAPE]:
                self.done = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
                self.cursor.click = True
                if self.cursor.action:
                    self.cursor.last_click = id(self.cursor.action)
                elif self.cursor.nav:
                    self.cursor.last_click = self.cursor.nav
                if event.button == 1:
                    self.logger.debug("LEFT MOUSE BUTTON DOWN")
                elif event.button == 3:
                    self.logger.debug("RIGHT MOUSE BUTTON DOWN")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.cursor.click = False
                if self.cursor.action and id(self.cursor.action) == self.cursor.last_click:
                    # A complete click has happened on an action zone.
                    self.logger.debug("FULL LEFT CLICK IN ACTION ZONE")
                    if "look" in self.cursor.action:
                        self.do_action("look")
                    elif "use" in self.cursor.action:
                        self.do_action("use")
                    elif "go" in self.cursor.action:
                        self.do_action("go")
                elif self.cursor.nav and self.cursor.nav == self.cursor.last_click:
                    # A complete click has happened on a navigation indicator.
                    self.logger.debug("FULL LEFT CLICK IN NAV REGION: {0}".format(self.cursor.nav))
                    if self.cursor.nav == "double":
                        self.world.navigate("forward")
                    else:
                        self.world.navigate(self.cursor.nav)
                    if self.text_dialog:
                        self.text_dialog.kill()
                        self.text_dialog = None
                elif self.cursor.pos:
                    if self.text_dialog:
                        self.text_dialog.kill()
                        self.text_dialog = None
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.cursor.click = False
                if self.cursor.action and id(self.cursor.action) == self.cursor.last_click:
                    self.logger.debug("FULL RIGHT CLICK IN ACTION ZONE")
                    if "use" in self.cursor.action:
                        self.do_action("use")
                    elif "go" in self.cursor.action:
                        self.do_action("go")
                elif self.cursor.nav in ["backward", "double"] and self.cursor.nav == self.cursor.last_click:
                    # We have right clicked on a backward or double arrow; attempt to go backward.
                    self.logger.debug("FULL RIGHT CLICK IN NAV REGION: {0}".format(self.cursor.nav))
                    self.world.navigate("backward")
                    if self.text_dialog:
                        self.text_dialog.kill()
                        self.text_dialog = None
                elif self.cursor.pos:
                    if self.text_dialog:
                        self.text_dialog.kill()
                        self.text_dialog = None
            elif event.type in (pygame.KEYUP, pygame.KEYDOWN):
                self.keys = pygame.key.get_pressed()
            self.gui.process_events(event)

    def demarc_action_indicator(self):
        """
        This is a method to demarcate an appropriate action indicator.
        For each action enumerated in the room, it figures out whether our cursor is in that action's region,
        And then updates the cursor object with the current action region if any, and draws the indicator.
        """
        x, y = self.cursor.pos

        if "actions" in self.world.room.vars:
            for action in self.world.room.vars["actions"]:
                rect = action["rect"]
                if "look" in action and "use" in action:
                    act_icon = "lookuse"
                elif "look" in action and "go" in action:
                    act_icon = "lookgo"
                elif "look" in action:
                    act_icon = "look"
                elif "use" in action:
                    act_icon = "use"
                elif "go" in action:
                    act_icon = "go"
                else:
                    return False
                if rect[0] < x < rect[2] and rect[1] < y < rect[3]:
                    blit_x = (rect[0] + ((rect[2] - rect[0]) // 2)) - (self.images[act_icon].get_width() // 2)
                    blit_y = (rect[1] + ((rect[3] - rect[1]) // 2)) - (self.images[act_icon].get_height() // 2)
                    blit_loc = (blit_x, blit_y)
                    self.screen.blit(self.images[act_icon], blit_loc)
                    self.cursor.action = action
                    return True
        self.cursor.action = None
        return False

    def demarc_nav_indicator(self):
        """
        This is a method to demarcate an appropriate navigation indicator.
        It does some irritating math to figure out if our cursor is in a region where a click would trigger navigation,
        And then updates the cursor object with the current navigation region if any, and draws the indicator.
        """
        wsize = self.config["window"]["size"]
        ss_min_x = wsize[0] * self.config["navigation"]["edge_margin_width"] // 1
        ss_max_x = wsize[0] - ss_min_x
        ss_region_left = wsize[0] * self.config["navigation"]["edge_region_breadth"] // 1
        ss_region_right = wsize[0] - ss_region_left
        ss_min_y = wsize[1] * self.config["navigation"]["edge_margin_width"] // 1
        ss_max_y = wsize[1] - ss_min_y
        ss_region_up = wsize[1] * self.config["navigation"]["edge_region_breadth"] // 1
        ss_region_down = wsize[1] - ss_region_up
        nf_min_x = wsize[0] // 2 - wsize[0] * self.config["navigation"]["forward_region_width"] // 2
        nf_max_x = wsize[0] // 2 + wsize[0] * self.config["navigation"]["forward_region_width"] // 2
        nf_min_y = wsize[1] // 2 - wsize[1] * self.config["navigation"]["forward_region_width"] // 2
        nf_max_y = wsize[1] // 2 + wsize[1] * self.config["navigation"]["forward_region_width"] // 2
        pad = self.config["navigation"]["indicator_padding"]
        x, y = self.cursor.pos

        # Calculate whether the mouse cursor is currently inside a navigation region.
        # If so, update the cursor with its current navigation region, and blit the nav indicator to the screen.
        if x < ss_region_left and ss_min_y < y < ss_max_y and "left" in self.world.room.vars["exits"]:
            blit_loc = (pad, wsize[1] // 2 - self.images["chevron_left"].get_height() // 2)
            self.screen.blit(self.images["chevron_left"], blit_loc)
            self.cursor.nav = "left"
        elif x > ss_region_right and ss_min_y < y < ss_max_y and "right" in self.world.room.vars["exits"]:
            blit_loc = (wsize[0] - self.images["chevron_right"].get_width() - pad,
                        wsize[1] // 2 - self.images["chevron_right"].get_height() // 2)
            self.screen.blit(self.images["chevron_right"], blit_loc)
            self.cursor.nav = "right"
        elif y < ss_region_up and ss_min_x < x < ss_max_x and "up" in self.world.room.vars["exits"]:
            blit_loc = (wsize[0] // 2 - self.images["chevron_up"].get_width() // 2, pad)
            self.screen.blit(self.images["chevron_up"], blit_loc)
            self.cursor.nav = "up"
        elif y > ss_region_down and ss_min_x < x < ss_max_x and "down" in self.world.room.vars["exits"]:
            blit_loc = (wsize[0] // 2 - self.images["chevron_down"].get_width() // 2,
                        wsize[1] - self.images["chevron_down"].get_height() - pad)
            self.screen.blit(self.images["chevron_down"], blit_loc)
            self.cursor.nav = "down"
        elif nf_min_x < x < nf_max_x and nf_min_y < y < nf_max_y and ("forward" in self.world.room.vars["exits"] or
                                                                      "backward" in self.world.room.vars["exits"]):
            if "forward" in self.world.room.vars["exits"] and "backward" in self.world.room.vars["exits"]:
                blit_loc = (wsize[0] // 2 - self.images["arrow_double"].get_width() // 2,
                            wsize[1] // 2 - self.images["arrow_double"].get_height() // 2)
                self.screen.blit(self.images["arrow_double"], blit_loc)
                self.cursor.nav = "double"
            elif "forward" in self.world.room.vars["exits"]:
                blit_loc = (wsize[0] // 2 - self.images["arrow_forward"].get_width() // 2,
                            wsize[1] // 2 - self.images["arrow_forward"].get_height() // 2)
                self.screen.blit(self.images["arrow_forward"], blit_loc)
                self.cursor.nav = "forward"
            elif "backward" in self.world.room.vars["exits"]:
                blit_loc = (wsize[0] // 2 - self.images["arrow_backward"].get_width() // 2,
                            wsize[1] // 2 - self.images["arrow_backward"].get_height() // 2)
                self.screen.blit(self.images["arrow_backward"], blit_loc)
                self.cursor.nav = "backward"
        else:
            self.cursor.nav = None

    def do_action(self, act_type):
        """
        Perform a room action, possibly creating a UI element.
        """
        wsize = self.config["window"]["size"]

        if self.cursor.action[act_type]["result"] == "text":
            self.logger.debug("ACTION TEXT RESULT CONTENTS: {0}".format(self.cursor.action[act_type]["contents"]))
            if self.text_dialog:
                self.text_dialog.kill()
                self.text_dialog = None
            gui_rect = pygame.Rect(self.config["gui"]["textbox_margin_sides"],
                                   wsize[1] - self.config["gui"]["textbox_margin_bottom"] -
                                   self.config["gui"]["textbox_height"],
                                   wsize[0] - self.config["gui"]["textbox_margin_sides"] * 2,
                                   self.config["gui"]["textbox_height"])
            self.text_dialog = pygame_gui.elements.ui_text_box.UITextBox(self.cursor.action[act_type]["contents"],
                                                                         gui_rect, self.gui)
        elif self.cursor.action[act_type]["result"] == "exit":
            self.logger.debug("ACTION EXIT RESULT CONTENTS: {0}".format(self.cursor.action[act_type]["contents"]))
            self.world.change_room(self.cursor.action[act_type]["contents"])

    def render(self):
        """
        All drawing should be found here.
        This is the only place that pygame.display.update() should be found.
        """
        self.screen.fill(pygame.Color("black"))
        self.screen.blit(self.world.room.image, (0, 0))
        if not self.demarc_action_indicator():
            self.demarc_nav_indicator()
        self.gui.draw_ui(self.screen)
        pygame.display.update()

    def main_loop(self):
        """
        This is the game loop for the entire program.
        Like the event_loop, there should not be more than one game_loop.
        """
        self.logger.info("Entering main loop.")
        while not self.done:
            self.event_loop()
            self.render()
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.cursor.update()
            self.gui.update(time_delta)
