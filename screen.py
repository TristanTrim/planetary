import pygame
from pygame.locals import SRCALPHA
from math import atan, degrees, radians
SCREEN_RES = (1024, 768)
CAPTION = "Planetary"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ARROW_TIP_SIZE = 10
REP_MARKER_SIZE = 0.2


class Screen():
	def __init__(self, sizes):
		pygame.init()
		self.window = pygame.display.set_mode(SCREEN_RES)
		pygame.display.set_caption(CAPTION.encode('utf-8'))
		pygame.display.flip()

		self.sizes = sizes


	def frame(self, objects, mouse_data):
		self.window.fill(BLACK)
		for object in objects:
			pygame.draw.circle(self.window, object.color, map(lambda x: int(x), object.pos), int(object.size))
			if object.mass < 0:
				pygame.draw.circle(self.window, WHITE, map(lambda x: int(x), object.pos), int(object.size * REP_MARKER_SIZE))
		
		if mouse_data['holding']:
			pygame.mouse.set_visible(False)
		else:
			pygame.mouse.set_visible(True)				

		if mouse_data['holding']:
			if mouse_data['size'] == 0:
				color = WHITE
			else:
				color = mouse_data['color']
			pygame.draw.circle(self.window, color, mouse_data['init_pos'], int(mouse_data['size']))
			pygame.draw.line(self.window, color, mouse_data['init_pos'], mouse_data['pos'])		
			if mouse_data['repulsor_mode']:
				pygame.draw.circle(self.window, WHITE, mouse_data['init_pos'], int(mouse_data['size'] * REP_MARKER_SIZE))	

			arrow_tip = pygame.Surface((ARROW_TIP_SIZE, ARROW_TIP_SIZE), SRCALPHA)			
			pygame.draw.polygon(arrow_tip, color, ((0, 0), (ARROW_TIP_SIZE, ARROW_TIP_SIZE/2), (0, ARROW_TIP_SIZE)))
			rel_pos = (mouse_data['pos'][0] - mouse_data['init_pos'][0], mouse_data['pos'][1] - mouse_data['init_pos'][1])
	
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
			self.window.blit(arrow_tip, (mouse_data['pos'][0]-(arrow_tip.get_width()/2), mouse_data['pos'][1]-(arrow_tip.get_height()/2)))

		pygame.display.flip()

	def get_events(self):
		return pygame.event.get()

	def get_mouse_pos(self):
		return pygame.mouse.get_pos()
	def get_mods(self):
		return pygame.key.get_mods()
