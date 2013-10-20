import pygame
from pygame.locals import SRCALPHA
from math import atan, degrees, radians
DEFAULT_SCREEN_RES = (1024, 768)
TEXT_OFFSET = (175, 25)
CAPTION = "Planetary"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ARROW_TIP_SIZE = 10
REP_MARKER_SIZE = 0.2
FONT_SIZE = 25
import itertools


##get us the project path, so we can open images easier.
import os
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

folders=(os.listdir(PROJECT_PATH+"/images/gifs/"))

##Loads all the images in images/gifs
sprites= {};
offset={};
frames={};
for i in folders:
  files =  os.listdir(PROJECT_PATH+"/images/gifs/"+i+"/")
  sprites[i]=[]
  offset[i]=(0,0)
  for frame in files:
      sprites[i].append(pygame.image.load(PROJECT_PATH+"/images/gifs/"+i+"/"+str(frame)))
  offset[i]=sprites[i][0].get_size()





class Screen():
	def __init__(self, sizes):
		pygame.init()
		self.screen_size = DEFAULT_SCREEN_RES
		self.window = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
		pygame.display.set_caption(CAPTION.encode('utf-8'))
		self.sizes = sizes
		pygame.font.init()
                self.font = pygame.font.Font(pygame.font.match_font(pygame.font.get_default_font()), FONT_SIZE)
		pygame.display.flip()


	def frame(self, objects, data, center):
		self.window.fill(BLACK)
		for object in objects:
                        
                        pos=[0,0]
                        pos[0]=object.pos[0]-(center[0])+(self.screen_size[1]/2)
                        pos[1]=object.pos[1]-(center[1])+(self.screen_size[1]/2)
                        if object.kind == "generic":
                            pygame.draw.circle(self.window, object.color, map(lambda x: int(x), pos), int(object.size))
                        if object.kind == "user":
                            pos[0]-(offset["WIKISHIP1GIF"][0]/2)
                            pos[1]-(offset["WIKISHIP1GIF"][1]/2)
                            self.window.blit(sprites["WIKISHIP1GIF"][4], pos)
                        else:
                            pygame.draw.circle(self.window, object.color, map(lambda x: int(x), pos), int(object.size))
#                        if object.isUser == True:
#                            pos[0]-16
#                            pos[1]-16
#                            self.window.blit(sprites["WIKISHIP1GIF"][4], pos)
#                        else:
#                            pygame.draw.circle(self.window, object.color, map(lambda x: int(x), pos), int(object.size))

		
		if data['holding']:
			pygame.mouse.set_visible(False)
		else:
			pygame.mouse.set_visible(True)				

		if data['holding']:
			if data['size'] == 0:
				color = WHITE
			else:
				color = data['color']

			pygame.draw.circle(self.window, color, data['init_pos'], int(data['size']))
			pygame.draw.line(self.window, color, data['init_pos'], data['pos'])		

			if data['repulsor_mode']:
				pygame.draw.circle(self.window, WHITE, data['init_pos'], int(data['size'] * REP_MARKER_SIZE))	

			arrow_tip = pygame.Surface((ARROW_TIP_SIZE, ARROW_TIP_SIZE), SRCALPHA)			
			pygame.draw.polygon(arrow_tip, color, ((0, 0), (ARROW_TIP_SIZE, ARROW_TIP_SIZE/2), (0, ARROW_TIP_SIZE)))
			rel_pos = (data['pos'][0] - data['init_pos'][0], data['pos'][1] - data['init_pos'][1])
	
			if rel_pos[0] == 0:
				if rel_pos[1] < 0:
					angle = radians(90)
				else:
					angle = radians(270)
			else:
				angle = -atan(rel_pos[1] / abs(float(rel_pos[0])))

			arrow_tip = pygame.transform.rotate(arrow_tip, degrees(angle))

			if rel_pos[0] < 0: 
				arrow_tip = pygame.transform.flip(arrow_tip, True, False)

			self.window.blit(arrow_tip, (data['pos'][0]-(arrow_tip.get_width()/2), data['pos'][1]-(arrow_tip.get_height()/2)))

		if data['text']:
			textbox = self.font.render(data['text'], True, WHITE, BLACK)
			self.window.blit(textbox, (self.screen_size[0] - TEXT_OFFSET[0], self.screen_size[1] - TEXT_OFFSET[1]))

		pygame.display.flip()

	def set_size(self, size):
		self.screen_size = size
		self.window = pygame.display.set_mode(size, pygame.RESIZABLE)
	def get_events(self):
		return pygame.event.get()
	def get_mouse_pos(self):
		return pygame.mouse.get_pos()
	def get_mods(self):
		return pygame.key.get_mods()
