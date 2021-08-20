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

import sys

import pygame

from lib.audiomanager import AudioManager
from lib.cursor import Cursor
from lib.logger import Logger
from lib.scriptmanager import ScriptManager
from lib.ui import UI
from lib.world import World


class App(object):
    """
    This class manages our event processing, game loop, and overall program flow.
    It is, for all intents and purposes, the base class. It contains a path to all other class instances.
    This class has no methods that are useful or available to event scripts.

    :ivar screen: The PyGame screen surface.
    :ivar clock: The PyGame Clock instance used for timing.
    :ivar fps: The base FPS of the engine. Currently hardcoded.
    :ivar done: If this becomes True, the engine will exit.
    :ivar keys: This always contains whichever keys are being pressed at the moment.
    :ivar cursor: The Cursor instance.
    :ivar config: This contains the engine's configuration variables.
    :ivar images: This is a dict containing all of the common required images.
    :ivar audio: The AudioManager instance.
    :ivar ui: The UI instance.
    :ivar resource: The ResourceManager instance.
    :ivar vars: A storage space for variables to be shared between event scripts.
    :ivar log: The Logger instance for this class.
    :ivar world: The World instance for the currently loaded world.
    :ivar script: The ScriptManager instance.
    """

    def __init__(self, screen, config, images, resource):
        """App Class Initializer

        :param screen: The PyGame screen surface.
        :param config: This contains the engine's configuration variables.
        :param images: This is a dict containing all of the common required images.
        :param resource: The ResourceManager instance.
        """
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.done = False
        self.keys = pygame.key.get_pressed()
        self.cursor = Cursor()
        self.config = config
        self.images = images
        self.audio = AudioManager(self.config)
        self.ui = UI(config, self.clock, self.fps, self.screen)
        self.resource = resource
        self.vars = {}
        self.log = Logger("App")

        # The game World must be initialized here, since it requires a reference to the App.
        self.log.info("Initializing game world...")
        self.world = World(config, self, resource)
        if not self.world.load():
            sys.exit(5)

        self.script = ScriptManager(self, self.audio, self.cursor, self.resource, self.ui, self.world)

    def __event_loop(self):
        """
        This is the event loop for the whole program.
        We handle clicks and navigation and cleaning up UI elements here.
        """
        # Iterate through current events, and process them.
        for event in pygame.event.get():
            # We have been asked to quit.
            if event.type == pygame.QUIT or self.keys[pygame.K_ESCAPE]:
                self.done = True

            # A left or right mouse button down event has been recorded.
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
                # Record that a click is in progress.
                self.cursor.click = True

                # If the cursor is in an action zone, make note of that zone.
                # This is necessary to check whether the cursor is in the same zone when click concludes.
                if self.cursor.action:
                    self.cursor.last_click = id(self.cursor.action)

                # If the cursor is in a navigation zone, make note of that zone.
                # This is necessary to check whether the cursor is in the same zone when click concludes.
                elif self.cursor.nav:
                    self.cursor.last_click = self.cursor.nav

                # For debugging purposes, log whether this is a left or a right click.
                if event.button == 1:
                    self.log.debug("LEFT MOUSE BUTTON DOWN")
                elif event.button == 3:
                    self.log.debug("RIGHT MOUSE BUTTON DOWN")

            # A left click has concluded.
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Record that no click is in progress anymore.
                self.cursor.click = False

                # The click was a complete click -- it started and ended within the same zone.
                # The zone was an action zone.
                if self.cursor.action and id(self.cursor.action) == self.cursor.last_click:
                    self.log.debug("FULL LEFT CLICK IN ACTION ZONE")

                    # Perform the action associated with this zone.
                    if "look" in self.cursor.action:
                        self.__do_action("look")
                    elif "use" in self.cursor.action:
                        self.__do_action("use")
                    elif "go" in self.cursor.action:
                        self.__do_action("go")

                # The click was a complete click -- it started and ended within the same zone.
                # The zone was a navigation zone.
                elif self.cursor.nav and self.cursor.nav == self.cursor.last_click:
                    self.log.debug("FULL LEFT CLICK IN NAV REGION: {0}".format(self.cursor.nav))

                    # Perform the navigation associated with the zone.
                    if self.cursor.nav == "double":
                        self.world.navigate("forward")
                    else:
                        self.world.navigate(self.cursor.nav)

                    # At the conclusion of changing rooms, the UI must be reset.
                    self.ui.reset()

                # We clicked somewhere other than a zone. Just reset the UI.
                elif self.cursor.pos:
                    self.ui.reset()

            # A right click has concluded.
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                # Record that no click is in progress anymore.
                self.cursor.click = False

                # The click was a complete click -- it started and ended within the same zone.
                # The zone was an action zone.
                if self.cursor.action and id(self.cursor.action) == self.cursor.last_click:
                    self.log.debug("FULL RIGHT CLICK IN ACTION ZONE")

                    # Perform the action associated with this zone.
                    if "use" in self.cursor.action:
                        self.__do_action("use")
                    elif "go" in self.cursor.action:
                        self.__do_action("go")

                # The click was a complete click -- it started and ended within the same zone.
                # The zone was a navigation zone.
                elif self.cursor.nav in ["backward", "double"] and self.cursor.nav == self.cursor.last_click:
                    # We have right clicked on a backward or double arrow; attempt to go backward.
                    self.log.debug("FULL RIGHT CLICK IN NAV REGION: {0}".format(self.cursor.nav))
                    self.world.navigate("backward")

                    # At the conclusion of changing rooms, the UI must be reset.
                    self.ui.reset()

                # We clicked somewhere other than a zone. Just reset the UI.
                elif self.cursor.pos:
                    self.ui.reset()

            # Record keypresses. We don't do anything with them yet.
            elif event.type in (pygame.KEYUP, pygame.KEYDOWN):
                self.keys = pygame.key.get_pressed()

            # Process any UI events that have been queued.
            self.ui._process_events(event)

    def __demarc_action_indicator(self) -> bool:
        """
        This is a method to demarcate an appropriate action indicator.
        For each action enumerated in the room, it figures out whether our cursor is in that action's region,
        And then updates the cursor object with the current action region if any, and draws the indicator.
        """
        x, y = self.cursor.pos

        # If the room file lists any actions, iterate through them.
        # For each, first figure out which icon to use for it,
        # And then figure out whether the mouse cursor is inside its zone.
        # If so, draw the action indicator onto the zone,
        # And then tell the Cursor which action zone it is inside.
        # If the Cursor is not inside any zone, tell it so.
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

    def __demarc_nav_indicator(self):
        """
        This is a method to demarcate an appropriate navigation indicator.
        It does some irritating math to figure out if our cursor is in a region where a click would trigger navigation,
        And then updates the cursor object with the current navigation region if any, and draws the indicator.
        """
        # Here we turn some small mathematical concepts into much smaller variables.
        # This makes the next block of code at least a little bit more readable.
        # Honestly I don't remember how all of this works right now, because I wrote it in deep flow.
        # Another harsh lesson in the virtue of writing comments as you go.
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

        # Calculate whether the mouse cursor is currently inside an existing navigation region.
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

    def __do_action(self, act_type: str):
        """
        Perform a room action, possibly creating a UI element.
        """
        # A text action was invoked. Create a textbox containing the contents.
        if self.cursor.action[act_type]["result"] == "text":
            self.log.debug("ACTION TEXT RESULT CONTENTS: {0}".format(self.cursor.action[act_type]["contents"]))
            self.ui.reset()
            self.ui.text_box(self.cursor.action[act_type]["contents"])

        # An exit action was invoked. Change rooms.
        elif self.cursor.action[act_type]["result"] == "exit":
            self.log.debug("ACTION EXIT RESULT CONTENTS: {0}".format(self.cursor.action[act_type]["contents"]))
            self.world.change_room(self.cursor.action[act_type]["contents"])

        # A script action was invoked. Execute an event script.
        elif self.cursor.action[act_type]["result"] == "script":
            self.log.debug("ACTION SCRIPT RESULT CONTENTS: {0}".format(self.cursor.action[act_type]["contents"]))
            try:
                script_result_split = self.cursor.action[act_type]["contents"].split(':')
                script_result_args = script_result_split[1].split(',')
            except IndexError:
                self.log.error("Malformed script result contents: {0}".format(self.cursor.action[act_type]["contents"]))
            else:
                self.script.call(script_result_split[0], *script_result_args)

    def __render(self):
        """
        Render a frame.
        """
        # Fill the screen with black, and then draw our room image.
        self.screen.fill(pygame.Color("black"))
        self.screen.blit(self.world.room.image, (0, 0))

        # If an action zone and a navigation zone overlap, the action zone always takes priority.
        # If no action zone was demarcated, only then will we demarcate a navigation zone.
        if not self.__demarc_action_indicator():
            self.__demarc_nav_indicator()

        # Draw the UI and update the display.
        self.ui._draw_ui()
        pygame.display.update()

    def _main_loop(self):
        """
        This is the main loop for the entire program.
        """
        self.log.info("Entering main loop.")

        # Until we are told to stop:
        # * Check for and process events.
        # * Render a frame.
        # * Update the Cursor.
        # * Update the UI.
        # * Run the AudioManager cleanup callback.
        while not self.done:
            self.__event_loop()
            self.__render()
            self.cursor._update()
            self.ui._update()
            self.audio._cleanup()
