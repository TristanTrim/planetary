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
BUTTON_FONT_SIZE = 25
POPUP_FONT_SIZE = 25
POPUP_SPACING = 10
GREY = (150, 150, 150)

TOOLBAR_WIDTH = 100

class events():
	STANDARD_MODE = 1

class GuiBox():
	def __init__(self, pos, size, border_color=WHITE, color=BLACK):
		self.pos = pos
		self.size = size
		self.border_color = border_color
		self.fill_color = color
		self.subelements = []

	def draw_border(self, surface, color):
		if not color:
			color = self.border_color
		
		pygame.draw.rect(surface, color, (0, 0, self.size[0], self.size[1]), 1)
	
	def draw(self, target):
		surface = pygame.Surface(self.size)

		if self.fill_color:
			surface.fill(self.fill_color)
		else:
			self.fill_color != BLACK


		for element in self.subelements:
			element.draw(surface)


		self.draw_border(surface, self.border_color)
		
		target.blit(surface, self.pos)

	def add_subelement(self, element):
		self.subelements.append(element)

class Button(GuiBox):
	def __init__(self, pos, size, event_down, content, state_count=0, toggleable=False, event_up=None, border_color=WHITE, color=BLACK, font_size=BUTTON_FONT_SIZE):
		self.pos = pos
		self.size = size
		self.border_color = border_color
		self.fill_color = color
		self.event_down = event_down
		self.toggleable = toggleable
		self.text = content #fixme
		self.active = False
                self.font = pygame.font.Font(pygame.font.match_font(pygame.font.get_default_font()), font_size)
		self.subelements = []

		if self.toggleable:
			assert state_count == 2
			self.event_up = event_up 

	def check(self):
		mouse_pos = pygame.mouse.get_pos()
		if (self.pos[0] < x < self.pos[0]+self.size[0] and self.pos[1] < y < self.pos[1]+self.size[1]):
				if not self.active:
					self.active = True
					pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'event': BUTTON_ACTIVE, 'source': self}))
				else:
					if self.active:
						self.active = False
						pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'event': BUTTON_INACTIVE, 'source': self}))		
	def click(self):
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'event': BUTTON_CLICK, 'source': self}))

	def draw(self, target):

		surface = pygame.Surface(self.size)
		for element in self.subelements:
			element.draw(surface)

		draw_color = self.border_color if not self.active else self.fill_color
		background_color = self.fill_color if not self.active else self.border_color

		if background_color:
			surface.fill(background_color)
		self.draw_border(surface, draw_color)
		text_surface = self.font.render(self.text, True, draw_color, background_color)
			
		surface.blit(text_surface, (surface.get_size()[0]/2 - text_surface.get_size()[0]/2, surface.get_size()[1]/2 - text_surface.get_size()[1]/2))
		pygame.image.save(surface, "a.png")

		target.blit(surface, self.pos)

class Popup(GuiBox):
	def __init__(self, text, option_text, options, anchor, offset, border_color=WHITE, text_color=WHITE, grey_color=GREY, background_color=BLACK, font_size=POPUP_FONT_SIZE, spacing = POPUP_SPACING):
		self.text = text
		self.option_text = option_text
		self.options = options
		self.anchor = anchor
		self.offset = offset
                self.font = pygame.font.Font(pygame.font.match_font(pygame.font.get_default_font()), font_size)
		self.border_color = border_color
		self.text_color = text_color
		self.grey_color = grey_color
		self.background_color = background_color
		self.spacing = spacing
				
		self.text_surface = self.multiline_render(self.text)
		self.option_text_surface = self.multiline_render(self.text)
		self.options_surface = self.multiline_render(self.text, self.anchor.popup_state)

		self.size = (max(self.text_surface.get_size()[0], self.option_text_surface.get_size()[0], self.options_surface.get_size()[0]), selftext_surface.get_size()[1] + self.option_test_suface.get_size()[1] + self.options_surface.get_size()[1] + self.spacing*2)
		self.pos = (self.anchor.pos[0] + self.offset[0], self.anchor.pos[1] + self.offset[1])

	def rerender_surfaces(self):
			self.options_surface = self.multiline_render(self.options, self.anchor.popup_state)
			self.option_text_surface = self.multiline_render(self.text)

	def multiline_render(self, text, hilight=None):
		line_surfaces = []
		for i, line in enumerate(self.text):
			if hilight != None:
				color = text_color if hilight == i else grey_color
			else:
				color = text_color
			line_surfaces.append(self.font.render(line, True, color, background_color))
		height = line_surfaces[0].get_size()[1]
		surface = pygame.Surface(len(line_surfaces) * height)
		for i, line in enumerate(line_surfaces):
			surface.blit(line, (0, height * i))
		return surface
			
	def draw(self, target):
		if self.anchor.popup_active:
			surface = pygame.Surface(self.size)
			self.draw_border(target, self.border_color)
			surface.blit(self.text_surface, (0, 0))
			surface.blit(self.option_text_surface, (0, self.text_surface.get_size[1] + self.spacing))
			surface.blit(self.options_surface, (0, self.size - self.options_surface.get_size()[1]))
			
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

		self.toolbar = GuiBox((0, 0), (TOOLBAR_WIDTH, self.screen_size[1]))
		self.toolbar.add_subelement(Button((0, 0), (TOOLBAR_WIDTH-20, TOOLBAR_WIDTH-20), events.STANDARD_MODE, "std"))		

	def frame(self, objects, data):
		self.window.fill(BLACK)
		self.toolbar.draw(self.window)

		for object in objects:
			pygame.draw.circle(self.window, object.color, map(lambda x: int(x), object.pos), int(object.size))
			if object.mass < 0:
				pygame.draw.circle(self.window, WHITE, map(lambda x: int(x), object.pos), int(object.size * REP_MARKER_SIZE))
		
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
