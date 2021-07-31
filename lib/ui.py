#####################
# BXEngine          #
# ui.py             #
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


class UI(object):
    def __init__(self, config, screen):
        self.config = config
        self.screen = screen
        self.pgui = pygame_gui.UIManager(self.config["window"]["size"])
        self.curr_dialog = None

    def _process_events(self, event):
        self.pgui.process_events(event)

    def _draw_ui(self):
        self.pgui.draw_ui(self.screen)

    def _update(self, time_delta):
        self.pgui.update(time_delta)

    def text_box(self, contents):
        wsize = self.config["window"]["size"]
        gui_rect = pygame.Rect(self.config["gui"]["textbox_margin_sides"],
                               wsize[1] - self.config["gui"]["textbox_margin_bottom"] -
                               self.config["gui"]["textbox_height"],
                               wsize[0] - self.config["gui"]["textbox_margin_sides"] * 2,
                               self.config["gui"]["textbox_height"])
        self.curr_dialog = pygame_gui.elements.ui_text_box.UITextBox(contents, gui_rect, self.pgui)

    def reset(self):
        if self.curr_dialog:
            self.curr_dialog.kill()
            self.curr_dialog = None
