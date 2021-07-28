#! /usr/bin/env python

"""
Started from example code written by Sean J. McKiernan 'Mekire'
* https://github.com/Mekire/pygame-samples/blob/master/drag_text.py
"""

import json
import os
import sys

import pygame as pg


CAPTION = "Backrooms Alpha"


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
		self.nav = None

	def update(self):
		self.pos = pg.mouse.get_pos()
		print(self.pos)


class App(object):
	"""
	A class to manage our event, game loop, and overall program flow.
	"""
	def __init__(self, config, images):
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
		self.config = config
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

	def demarc_nav_indicator(self):
		"""
		This is a method to demarcate an appropriate nagigation indicator.
		It does some irritating math to figure out if our cursor is in a region where a click would trigger navigation,
		And then updates the cursor object with the current navigation region if any, and draws the indicator.
		"""
		ss_min_x = self.config["window"]["size"][0] * self.config["navigation"]["edge_margin_width"] // 1
		ss_max_x = self.config["window"]["size"][0] - ss_min_x
		ss_region_left = self.config["window"]["size"][0] * self.config["navigation"]["edge_region_breadth"] // 1
		ss_region_right = self.config["window"]["size"][0] - ss_region_left
		ss_min_y = self.config["window"]["size"][1] * self.config["navigation"]["edge_margin_width"] // 1
		ss_max_y = self.config["window"]["size"][1] - ss_min_y
		ss_region_up = self.config["window"]["size"][1] * self.config["navigation"]["edge_region_breadth"] // 1
		ss_region_down = self.config["window"]["size"][1] - ss_region_up
		
		x, y = self.cursor.pos
		
		if x < ss_region_left and ss_min_y < y < ss_max_y:
			blit_loc = (10, self.config["window"]["size"][1] // 2 - self.images["chevron_left"].get_height() // 2)
			self.screen.blit(self.images["chevron_left"], blit_loc)
			self.cursor.nav = "left"
		elif x > ss_region_right and ss_min_y < y < ss_max_y:
			blit_loc = (self.config["window"]["size"][0] - self.images["chevron_right"].get_width() - 10, self.config["window"]["size"][1] // 2 - self.images["chevron_right"].get_height() // 2)
			self.screen.blit(self.images["chevron_right"], blit_loc)
			self.cursor.nav = "right"
		elif y < ss_region_up and ss_min_x < x < ss_max_x:
			blit_loc = (self.config["window"]["size"][0] // 2 - self.images["chevron_up"].get_width() // 2, 10)
			self.screen.blit(self.images["chevron_up"], blit_loc)
			self.cursor.nav = "up"
		elif y > ss_region_down and ss_min_x < x < ss_max_x:
			blit_loc = (self.config["window"]["size"][0] // 2 - self.images["chevron_down"].get_width() // 2, self.config["window"]["size"][1] - self.images["chevron_down"].get_height() - 10)
			self.screen.blit(self.images["chevron_down"], blit_loc)
			self.cursor.nav = "down"
		else:
			self.cursor.nav = None
		
	def render(self):
		"""
		All drawing should be found here.
		This is the only place that pygame.display.update() should be found.
		"""
		self.screen.fill(pg.Color("black"))
		self.screen.blit(self.images["room"], (0,0))
		self.demarc_nav_indicator()
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
	with open("config.json") as f:
		config = json.load(f)
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pg.init()
	pg.display.set_caption(CAPTION)
	pg.display.set_mode(config["window"]["size"])
	
	images["room"] = pg.transform.scale(pg.image.load("room1.jpg"), config["window"]["size"])
	images["chevron_left"] = pg.transform.scale(pg.image.load("chevron_left.png"), config["navigation"]["indicator_size"])
	images["chevron_right"] = pg.transform.scale(pg.image.load("chevron_right.png"), config["navigation"]["indicator_size"])
	images["chevron_up"] = pg.transform.scale(pg.image.load("chevron_up.png"), config["navigation"]["indicator_size"])
	images["chevron_down"] = pg.transform.scale(pg.image.load("chevron_down.png"), config["navigation"]["indicator_size"])
	
	App(config, images).main_loop()
	pg.quit()
	sys.exit()
	

if __name__ == "__main__":
	main()
