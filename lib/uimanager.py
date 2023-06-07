##################
# BXEngine       #
# uimanager.py   #
# Copyright 2021 #
# Sei Satzparad  #
##################

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

from lib.logger import Logger


class UIManager(object):
    """The UI Manager

    This class handles the creation and placement of UI elements.

    :ivar config: This contains the engine's configuration variables.
    :ivar clock: The PyGame clock.
    :ivar fps: The fps setting of the engine.
    :ivar screen: The PyGame screen surface.
    :ivar pgui: The PyGame GUI library's internal UI Manager.
    :ivar curr_dialog: Object for the currently visible/active UI element.
    :ivar log: The Logger instance for this class.
    """
    def __init__(self, config, clock, fps, screen):
        """UIManager Class Initializer

        :param config: This contains the engine's configuration variables.
        :param clock: The PyGame clock.
        :param fps: The fps setting of the engine.
        :param screen: The PyGame screen surface.
        """
        self.config = config
        self.clock = clock
        self.fps = fps
        self.screen = screen
        self.pgui = pygame_gui.UIManager(self.config["window"]["size"])
        self.curr_dialog = None
        self.log = Logger("UI")

    def _process_events(self, event):
        """Call PyGame GUI to process an event.

        :param event: PyGame GUI internal event.
        """
        self.pgui.process_events(event)

    def _draw_ui(self):
        """Call PyGame GUI to draw to the screen.
        """
        self.pgui.draw_ui(self.screen)

    def _update(self):
        """Call PyGame GUI to update / perform a tick.
        """
        self.pgui.update(self.clock.tick(self.fps) / 1000.0)

    def _refresh(self):
        """Refresh what is drawn and call PyGame GUI to update.
        """
        self._update()
        self._draw_ui()
        pygame.display.update()

    def text_box(self, contents: str):
        """Draw string contents to a text dialog on screen.

        :param contents: A string containing the contents to be drawn to the text box.
        """
        wsize = self.config["window"]["size"]
        gui_rect = pygame.Rect(self.config["gui"]["textbox_margin_sides"],
                               wsize[1] - self.config["gui"]["textbox_margin_bottom"] -
                               self.config["gui"]["textbox_height"],
                               wsize[0] - self.config["gui"]["textbox_margin_sides"] * 2,
                               self.config["gui"]["textbox_height"])
        self.curr_dialog = pygame_gui.elements.ui_text_box.UITextBox(contents, gui_rect, self.pgui)
        self._refresh()
        self.log.info("text_box(): Drew text box with contents: {0}".format(contents))

    def reset(self):
        """Delete the currently active UI element.
        """
        if self.curr_dialog:
            self.curr_dialog.kill()
            self.curr_dialog = None
