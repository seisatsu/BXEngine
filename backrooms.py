#! /usr/bin/env python

"""
Started from example code written by Sean J. McKiernan 'Mekire'
* https://github.com/Mekire/pygame-samples/blob/master/drag_text.py
"""

import os
import sys

import pygame as pg


CAPTION = "Backrooms Alpha"
SCREEN_SIZE = (800, 600)


class Cursor(object):
	"""
	A class to represent our lovable red sqaure.
	"""
	
	def __init__(self):
		"""
		The argument pos corresponds to the center of our rectangle.
		"""
		self.click = False
		self.pos = [0, 0]

	def update(self):
		self.pos = pg.mouse.get_pos()
		print(self.pos)


class App(object):
	"""
	A class to manage our event, game loop, and overall program flow.
	"""
	def __init__(self, images):
		"""
		Get a reference to the screen (created in main); define necessary
		attributes; and create our player (draggable rect).
		"""
		self.screen = pg.display.get_surface()
		self.screen_rect = self.screen.get_rect()
		self.clock = pg.time.Clock()
		self.fps = 60
		self.done = False
		self.keys = pg.key.get_pressed()
		self.cursor = Cursor()
		self.images = images

	def event_loop(self):
		"""
		This is the event loop for the whole program.
		Regardless of the complexity of a program, there should never be a need
		to have more than one event loop.
		"""
		for event in pg.event.get():
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
				self.done = True
			elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
				self.cursor.click = True
				print("CLICK")
			elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
				self.cursor.click = False
			elif event.type in (pg.KEYUP, pg.KEYDOWN):
				self.keys = pg.key.get_pressed() 

	def draw_nav_ind(self):
		"""
		This is a method to draw an appropriate nagigation indicator.
		"""
		ss_min_x = SCREEN_SIZE[0] // 4
		ss_max_x = SCREEN_SIZE[0] // 4 * 3
		ss_margin_left = SCREEN_SIZE[0] // 8
		ss_margin_right = SCREEN_SIZE[0] // 8 * 7
		ss_min_y = SCREEN_SIZE[1] // 4
		ss_max_y = SCREEN_SIZE[1] // 4 * 3
		ss_margin_up = SCREEN_SIZE[1] // 8
		ss_margin_down = SCREEN_SIZE[1] // 8 * 7
		
		x, y = self.cursor.pos
		
		if x < ss_margin_left and ss_margin_up < y < ss_margin_down:
			blit_loc = (10, SCREEN_SIZE[1] // 2 - self.images["chevron_left"].get_height() // 2)
			self.screen.blit(self.images["chevron_left"], blit_loc)
		elif x > ss_margin_right and ss_margin_up < y < ss_margin_down:
			blit_loc = (SCREEN_SIZE[0] - self.images["chevron_right"].get_width() - 10, SCREEN_SIZE[1] // 2 - self.images["chevron_right"].get_height() // 2)
			self.screen.blit(self.images["chevron_right"], blit_loc)
		elif y < ss_margin_up and ss_margin_left < x < ss_margin_right:
			blit_loc = (SCREEN_SIZE[0] // 2 - self.images["chevron_up"].get_width() // 2, 10)
			self.screen.blit(self.images["chevron_up"], blit_loc)
		elif y > ss_margin_down and ss_margin_left < x < ss_margin_right:
			blit_loc = (SCREEN_SIZE[0] // 2 - self.images["chevron_down"].get_width() // 2, SCREEN_SIZE[1] - self.images["chevron_down"].get_height() - 10)
			self.screen.blit(self.images["chevron_down"], blit_loc)
		
	def render(self):
		"""
		All drawing should be found here.
		This is the only place that pygame.display.update() should be found.
		"""
		self.screen.fill(pg.Color("black"))
		self.screen.blit(self.images["room"], (0,0))
		self.draw_nav_ind()
		pg.display.update()

	def main_loop(self):
		"""
		This is the game loop for the entire program.
		Like the event_loop, there should not be more than one game_loop.
		"""
		while not self.done:
			self.event_loop()
			self.render()
			self.clock.tick(self.fps)
			self.cursor.update()


def main():
	"""
	Prepare our environment, create a display, and start the program.
	"""
	images = {}
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption(CAPTION)
	pg.display.set_mode(SCREEN_SIZE)
	
	images["room"] = pg.image.load("room1.jpg")
	images["chevron_left"] = pg.image.load("chevron_left.png")
	images["chevron_right"] = pg.image.load("chevron_right.png")
	images["chevron_up"] = pg.image.load("chevron_up.png")
	images["chevron_down"] = pg.image.load("chevron_down.png")
	
	App(images).main_loop()
	pg.quit()
	sys.exit()
	

if __name__ == "__main__":
	main()
