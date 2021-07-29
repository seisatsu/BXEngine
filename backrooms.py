#! /usr/bin/env python

"""
Started from example code written by Sean J. McKiernan 'Mekire'
* https://github.com/Mekire/pygame-samples/blob/master/drag_text.py
"""

import json
import os
import sys

import pygame
import pygame_gui


CAPTION = "Backrooms Alpha"


class Cursor(object):
	"""
	A class to represent our cursor.
	"""
	
	def __init__(self):
		"""
		Stuff here.
		"""
		self.click = False
		self.last_click = None
		self.pos = [0, 0]
		self.nav = None
		self.action = None

	def update(self):
		self.pos = pygame.mouse.get_pos()


class World(object):
	"""
	A class to represent the game world.
	"""
	def __init__(self, config):
		self.config = config
		self.dir = self.config["world"]
		self.vars = None
		self.room = None
	
	def load(self):
		with open("{0}/world.json".format(self.dir)) as f:
			self.vars = json.load(f)
		self.change_room(self.vars["first_room"])
	
	def navigate(self, direction):
		if direction in self.room.vars["exits"]:
			self.change_room(self.room.vars["exits"][direction])
	
	def change_room(self, room_file):
		self.room = Room(self.config, self, room_file)
		self.room.load()


class Room(object):
	"""
	A class to represent the current room.
	"""
	def __init__(self, config, world, room_file):
		self.config = config
		self.world = world
		self.file = room_file
		self.vars = None
		self.image = None
	
	def load(self):
		with open("{0}/{1}".format(self.world.dir, self.file)) as f:
			self.vars = json.load(f)
		self.image = pygame.transform.scale(pygame.image.load(resource_path("{0}/{1}".format(self.world.dir, self.vars["image"]))), self.config["window"]["size"])


class App(object):
	"""
	A class to manage our event, game loop, and overall program flow.
	"""
	def __init__(self, config, images, world, gui):
		"""
		Get a reference to the screen (created in main); define necessary
		attributes.
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
		self.text_dialog = None

	def event_loop(self):
		"""
		This is the event loop for the whole program.
		Regardless of the complexity of a program, there should never be a need
		to have more than one event loop.
		We handle clicks and navigation and cleaning up UI elements here.
		"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT or self.keys[pygame.K_ESCAPE]:
				self.done = True
			elif event.type == pygame.MOUSEBUTTONDOWN and event.button in [1, 3]:
				self.cursor.click = True
				self.cursor.last_click = self.cursor.pos
				print("CLICK")
			elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
				self.cursor.click = False
				if self.cursor.pos == self.cursor.last_click and self.cursor.action:
					# A complete click has happened on an action zone.
					print("FULL LEFT CLICK IN ACTION ZONE")
					if "look" in self.cursor.action:
						self.do_action("look")
					elif "use" in self.cursor.action:
						self.do_action("use")
					elif "go" in self.cursor.action:
						self.do_action("go")
				elif self.cursor.pos == self.cursor.last_click and self.cursor.nav:
					# A complete click has happened on a navigation indicator.
					print("FULL LEFT CLICK IN NAV REGION {0}".format(self.cursor.nav))
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
				if self.cursor.pos == self.cursor.last_click and self.cursor.action:
					print("FULL RIGHT CLICK IN ACTION ZONE")
					if "use" in self.cursor.action:
						self.do_action("use")
					elif "go" in self.cursor.action:
						self.do_action("go")
				elif self.cursor.pos == self.cursor.last_click and self.cursor.nav in ["backward", "double"]:
					# We have right clicked on a backward or double arrow; attempt to go backward.
					print("FULL RIGHT CLICK IN NAV REGION {0}".format(self.cursor.nav))
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
		ss_min_x = self.config["window"]["size"][0] * self.config["navigation"]["edge_margin_width"] // 1
		ss_max_x = self.config["window"]["size"][0] - ss_min_x
		ss_region_left = self.config["window"]["size"][0] * self.config["navigation"]["edge_region_breadth"] // 1
		ss_region_right = self.config["window"]["size"][0] - ss_region_left
		ss_min_y = self.config["window"]["size"][1] * self.config["navigation"]["edge_margin_width"] // 1
		ss_max_y = self.config["window"]["size"][1] - ss_min_y
		ss_region_up = self.config["window"]["size"][1] * self.config["navigation"]["edge_region_breadth"] // 1
		ss_region_down = self.config["window"]["size"][1] - ss_region_up
		nf_min_x = self.config["window"]["size"][0] // 2 - self.config["window"]["size"][0] * self.config["navigation"]["forward_region_width"] // 2
		nf_max_x = self.config["window"]["size"][0] // 2 + self.config["window"]["size"][0] * self.config["navigation"]["forward_region_width"] // 2
		nf_min_y = self.config["window"]["size"][1] // 2 - self.config["window"]["size"][1] * self.config["navigation"]["forward_region_width"] // 2
		nf_max_y = self.config["window"]["size"][1] // 2 + self.config["window"]["size"][1] * self.config["navigation"]["forward_region_width"] // 2
		pad = self.config["navigation"]["indicator_padding"]
		
		x, y = self.cursor.pos
		
		if x < ss_region_left and ss_min_y < y < ss_max_y and "left" in self.world.room.vars["exits"]:
			blit_loc = (pad, self.config["window"]["size"][1] // 2 - self.images["chevron_left"].get_height() // 2)
			self.screen.blit(self.images["chevron_left"], blit_loc)
			self.cursor.nav = "left"
		elif x > ss_region_right and ss_min_y < y < ss_max_y and "right" in self.world.room.vars["exits"]:
			blit_loc = (self.config["window"]["size"][0] - self.images["chevron_right"].get_width() - pad, self.config["window"]["size"][1] // 2 - self.images["chevron_right"].get_height() // 2)
			self.screen.blit(self.images["chevron_right"], blit_loc)
			self.cursor.nav = "right"
		elif y < ss_region_up and ss_min_x < x < ss_max_x and "up" in self.world.room.vars["exits"]:
			blit_loc = (self.config["window"]["size"][0] // 2 - self.images["chevron_up"].get_width() // 2, pad)
			self.screen.blit(self.images["chevron_up"], blit_loc)
			self.cursor.nav = "up"
		elif y > ss_region_down and ss_min_x < x < ss_max_x and "down" in self.world.room.vars["exits"]:
			blit_loc = (self.config["window"]["size"][0] // 2 - self.images["chevron_down"].get_width() // 2, self.config["window"]["size"][1] - self.images["chevron_down"].get_height() - pad)
			self.screen.blit(self.images["chevron_down"], blit_loc)
			self.cursor.nav = "down"
		elif nf_min_x < x < nf_max_x and nf_min_y < y < nf_max_y and ("forward" in self.world.room.vars["exits"] or "backward" in self.world.room.vars["exits"]):
			if "forward" in self.world.room.vars["exits"] and "backward" in self.world.room.vars["exits"]:
				blit_loc = (self.config["window"]["size"][0] // 2 - self.images["arrow_double"].get_width() // 2, self.config["window"]["size"][1] // 2 - self.images["arrow_double"].get_height() // 2)
				self.screen.blit(self.images["arrow_double"], blit_loc)
				self.cursor.nav = "double"
			elif "forward" in self.world.room.vars["exits"]:
				blit_loc = (self.config["window"]["size"][0] // 2 - self.images["arrow_forward"].get_width() // 2, self.config["window"]["size"][1] // 2 - self.images["arrow_forward"].get_height() // 2)
				self.screen.blit(self.images["arrow_forward"], blit_loc)
				self.cursor.nav = "forward"
			elif "backward" in self.world.room.vars["exits"]:
				blit_loc = (self.config["window"]["size"][0] // 2 - self.images["arrow_backward"].get_width() // 2, self.config["window"]["size"][1] // 2 - self.images["arrow_backward"].get_height() // 2)
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
			print(self.cursor.action[act_type]["contents"])
			if self.text_dialog:
				self.text_dialog.kill()
				self.text_dialog = None
			gui_rect = pygame.Rect(self.config["gui"]["textbox_margin_sides"], wsize[1] - self.config["gui"]["textbox_margin_bottom"] - self.config["gui"]["textbox_height"],
						wsize[0] - self.config["gui"]["textbox_margin_sides"] * 2, self.config["gui"]["textbox_height"])
			self.text_dialog = pygame_gui.elements.ui_text_box.UITextBox(self.cursor.action[act_type]["contents"], gui_rect, self.gui)
		elif self.cursor.action[act_type]["result"] == "exit":
			print(self.cursor.action[act_type]["contents"])
			self.world.change_room(self.cursor.action[act_type]["contents"])
			

	def render(self):
		"""
		All drawing should be found here.
		This is the only place that pygame.display.update() should be found.
		"""
		self.screen.fill(pygame.Color("black"))
		self.screen.blit(self.world.room.image, (0,0))
		if not self.demarc_action_indicator():
			self.demarc_nav_indicator()
		self.gui.draw_ui(self.screen)
		pygame.display.update()

	def main_loop(self):
		"""
		This is the game loop for the entire program.
		Like the event_loop, there should not be more than one game_loop.
		"""
		while not self.done:
			self.event_loop()
			self.render()
			time_delta = self.clock.tick(self.fps) / 1000.0
			self.cursor.update()
			self.gui.update(time_delta)


def resource_path(relative_path):
	"""
	Thanks to https://stackoverflow.com/questions/54210392/how-can-i-convert-pygame-to-exe
	"""
	try:
	# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)


def load_config():
	with open("config.json") as f:
		config = json.load(f)
	return config


def load_images(config):
	images = {}
	images["chevron_left"] = pygame.transform.scale(pygame.image.load(resource_path("images/chevron_left.png")), config["navigation"]["indicator_size"])
	images["chevron_right"] = pygame.transform.scale(pygame.image.load(resource_path("images/chevron_right.png")), config["navigation"]["indicator_size"])
	images["chevron_up"] = pygame.transform.scale(pygame.image.load(resource_path("images/chevron_up.png")), config["navigation"]["indicator_size"])
	images["chevron_down"] = pygame.transform.scale(pygame.image.load(resource_path("images/chevron_down.png")), config["navigation"]["indicator_size"])
	images["arrow_forward"] = pygame.transform.scale(pygame.image.load(resource_path("images/arrow_forward.png")), config["navigation"]["indicator_size"])
	images["arrow_backward"] = pygame.transform.scale(pygame.image.load(resource_path("images/arrow_backward.png")), config["navigation"]["indicator_size"])
	images["arrow_double"] = pygame.transform.scale(pygame.image.load(resource_path("images/arrow_double.png")), config["navigation"]["indicator_size"])
	images["look"] = pygame.transform.scale(pygame.image.load(resource_path("images/look.png")), config["navigation"]["indicator_size"])
	images["use"] = pygame.transform.scale(pygame.image.load(resource_path("images/use.png")), config["navigation"]["indicator_size"])
	images["lookuse"] = pygame.transform.scale(pygame.image.load(resource_path("images/lookuse.png")), config["navigation"]["indicator_size"])
	images["go"] = pygame.transform.scale(pygame.image.load(resource_path("images/go.png")), config["navigation"]["indicator_size"])
	images["lookgo"] = pygame.transform.scale(pygame.image.load(resource_path("images/lookgo.png")), config["navigation"]["indicator_size"])
	return images


def main():
	"""
	Prepare our environment, create a display, and start the program.
	"""
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	
	config = load_config()
	images = load_images(config)
	
	pygame.display.set_caption(CAPTION)
	pygame.display.set_mode(config["window"]["size"])
	gui = pygame_gui.UIManager(config["window"]["size"])
	
	world = World(config)
	world.load()
	App(config, images, world, gui).main_loop()
	pygame.quit()
	sys.exit()
	

if __name__ == "__main__":
	main()

