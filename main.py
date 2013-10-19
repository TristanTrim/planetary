import screen
from pygame.time import Clock
from pygame.locals import *
from math import sqrt
from random import randint, uniform


FRAMERATE_VALUES = [20, 30, 60]
DEFAULT_FRAMERATE_SETTING = 2
BASE_SPAWN_RATE = FRAMERATE_VALUES[DEFAULT_FRAMERATE_SETTING]
FRAMERATE_LABELS = ['Low', 'Medium', 'High']
TIME_RATIO = 1.5 # more = slower simulation
NUMBER_KEYS = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
MASS_VALUES = [1000 * 2**x for x in range(10)]
MASS_VALUES[0] = 0
SIZE_FACTOR = 0.5
SIZE_VALUES = [SIZE_FACTOR * pow(x, 1/3.0) for x in MASS_VALUES]
DELETE_MARGIN = [1, 1]
from screen import DEFAULT_SCREEN_RES as screen_size
G = 4
WHITE = (255, 255, 255)
settings = {'paused': False, 'gravity-min': True, 'gravity-maj': True, 'framerate': DEFAULT_FRAMERATE_SETTING}
timefactor = TIME_RATIO / FRAMERATE_VALUES[settings['framerate']]
SWARM_MAX_VEL = 10
SWARM_COUNT = 10
SPAWNER_DELETE_DISTANCE = 25
TEXT_TIMEOUT = 4

class Spawner():
	def __init__(self, position, obj_velocity, intensity):
		self.pos = position
		self.o_vel = obj_velocity
		self.intensity = intensity
		self.spawn_counter = 0

	def delete(self):
		global spawners
		spawners.remove(self)

	def spawn(self):
		self.spawn_counter += self.intensity * BASE_SPAWN_RATE
		global minor_objects
		while self.spawn_counter > FRAMERATE_VALUES[settings['framerate']]:
			velocity = list(self.o_vel)
			velocity[0] += uniform(-SWARM_MAX_VEL, SWARM_MAX_VEL)
			velocity[1] += uniform(-SWARM_MAX_VEL, SWARM_MAX_VEL)

			object = Object(self.pos, velocity)
			minor_objects.append(object)
			self.spawn_counter -= FRAMERATE_VALUES[settings['framerate']]

class Object():
	def __init__(self, position, velocity, color=WHITE, mass=0):
		self.pos = list(position)
		self.vel = list(velocity)
		self.color = color 
		self.mass = mass 
		self.size = 0.5 * pow(abs(mass), 1/3.0)	
		self.isUser = 0
		
	def delete(self):
		if self.mass:
			global major_objects
			if self in major_objects:
				major_objects.remove(self)
		else:
			global minor_objects
			if self in minor_objects:
				minor_objects.remove(self)

	def tick(self, attractors):
		if self.pos[0] > (DELETE_MARGIN[0]+1) * screen_size[0]:
			self.delete()
			return
		if self.pos[0] < -DELETE_MARGIN[0] * screen_size[0]:
			self.delete()
			return
		if self.pos[1] > (DELETE_MARGIN[1]+1) * screen_size[1]:
			self.delete()
			return
		if self.pos[1] < -DELETE_MARGIN[1] * screen_size[1]:
			self.delete()
			return

		self.gravity = [0, 0]

		for object in attractors:
			if object == self:
				continue

			distance = sqrt( ((self.pos[0] - object.pos[0])**2) + ((self.pos[1] - object.pos[1])**2))
					
			if self.mass == 0 and distance < object.size:
				self.delete()	
				return

			if distance < (self.size + object.size) and self.mass >= object.mass and (self.mass or object.mass):
				if self.mass == -object.mass:
					object.delete()
					self.delete()
					return

				new_velocity = [0, 0]
				new_velocity[0] = (self.vel[0] * self.mass + object.vel[0] * object.mass) / (self.mass + object.mass)
				new_velocity[1] = (self.vel[1] * self.mass + object.vel[1] * object.mass) / (self.mass + object.mass)
				new_color = [0, 0, 0]
				new_color[0] = (self.color[0] * self.mass + object.color[0] * object.mass) / (self.mass + object.mass)
				new_color[1] = (self.color[1] * self.mass + object.color[1] * object.mass) / (self.mass + object.mass)
				new_color[2] = (self.color[2] * self.mass + object.color[2] * object.mass) / (self.mass + object.mass)
				new_color = map(lambda x: max(min(255, x), 0), new_color)
			
				new_object = Object(self.pos, new_velocity,  new_color, self.mass + object.mass)
				object.delete()
				self.delete()
				new_object.tick(major_objects)
				major_objects.append(new_object)	
				return

			if (settings['gravity-min'] and self.mass == 0) or (settings['gravity-maj'] and self.mass):
				self.gravity[0] -= (G * object.mass * (self.pos[0] - object.pos[0])) / distance**3
				self.gravity[1] -= (G * object.mass * (self.pos[1] - object.pos[1])) / distance**3
			
		#if the object is a minor object (i.e. has no gravitational field), it is safe to update it immediately: 
		if self.mass == 0:
			self.update()	

	def update(self):		
		self.vel[0] += self.gravity[0] * timefactor
		self.vel[1] += self.gravity[1] * timefactor

		if self.isUser == 1:
			self.vel[0] += InputHandler.user_left_right * timefactor
			self.vel[1] += InputHandler.user_up_down * timefactor
			print("vel is " + str(InputHandler.user_left_right) +", "+str(InputHandler.user_up_down))
		
		self.pos[0] += self.vel[0] * timefactor
		self.pos[1] += self.vel[1] * timefactor


class InputHandler():
	def __init__(self):
		self.mouse_pos = (0, 0)
		self.mouse_initial_pos = (0, 0)
		self.mouse_holding = False
		self.mass_selection = 0
		self.display_data = {'holding': False, 'init_pos': (0, 0), 'pos': (0, 0), 'size': 0}
		self.next_color = (randint(0, 255), randint(0, 255), randint(0, 255))
		self.repulsor_mode = False
		self.text = ''
		self.text_timeout = 0
		self.manual_spawner = None

		self.user_left_right = 0
		self.user_up_down = 0


	def handle_input(self, Screen):
		def distance(object):
			return sqrt( (self.mouse_pos[0] - object.pos[0])**2 + (self.mouse_pos[1] - object.pos[1]) **2)

		events = Screen.get_events()
		self.mouse_pos = Screen.get_mouse_pos()
		global major_objects, minor_objects, settings

		for event in events:
			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					found = False
					for object in major_objects:
						if distance(object) < object.size:
							object.vel = [0, 0]
							found = True
					if not found:
						if self.manual_spawner:
							self.add_spawner()
						else:
							self.mouse_initial_pos = self.mouse_pos
							self.mouse_holding = True

				elif event.button == 3:
					if self.mouse_holding:
						self.mouse_holding = False
					else:
						for object in major_objects:
							if distance(object) < object.size:
								object.delete()

						for spawner in spawners:
							if distance(spawner) < SPAWNER_DELETE_DISTANCE:
								spawner.delete()

				elif event.button == 4:
					self.mass_selection = min(self.mass_selection+1, 9)
				elif event.button == 5:
					self.mass_selection = max(self.mass_selection-1, 0)

			elif event.type == MOUSEBUTTONUP and event.button == 1 and self.mouse_holding:
				self.mouse_holding = False
				if not self.manual_spawner:
					self.add_object()

			elif event.type == KEYDOWN:
				if event.key in NUMBER_KEYS:
					self.mass_selection = NUMBER_KEYS.index(event.key)
				elif event.key == K_p:
					settings['paused'] = not settings['paused']
				elif event.key == K_g:
					settings['gravity-maj'] = not settings['gravity-maj']
				elif event.key == K_h:
					settings['gravity-min'] = not settings['gravity-min']
				elif event.key == K_f:
					settings['framerate'] = (settings['framerate'] + 1) % len(FRAMERATE_VALUES)
					global timefactor
					timefactor = TIME_RATIO / FRAMERATE_VALUES[settings['framerate']]
					self.text = "Framerate:" + FRAMERATE_LABELS[settings['framerate']]	
					self.text_timeout = 0
				elif event.key == K_z:
					minor_objects = []
				elif event.key == K_x:
					major_objects = []
				elif event.key == K_s:
					self.manual_spawner = Spawner(self.mouse_pos, (0, 0), 1) 
				elif event.key == K_q:
					found = False
					for object in major_objects:
						if distance(object) < object.size:
							object.mass = -object.mass
							found = True
					if not found:
						self.repulsor_mode = not self.repulsor_mode
				## user controlls ##
				elif event.key == K_u:
					self.add_object(isUser=1)
				elif event.key == K_UP:
					self.user_up_down = -100
					print("up")
				elif event.key == K_DOWN:
					self.user_up_down = 100
					print("down")
				elif event.key == K_LEFT:
					self.user_left_right = -100
					print("left")
				elif event.key == K_RIGHT:
					self.user_left_right = 100
					print("right")
				## ##

			elif event.type == KEYUP:
				if event.key == K_s:
					self.manual_spawner = None
				## kill user keypress ##
				elif event.key == K_UP:
					self.user_up_down = 0
					print("up")
				elif event.key == K_DOWN:
					self.user_up_down = 0
					print("down")
				elif event.key == K_LEFT:
					self.user_left_right = 0
					print("left")
				elif event.key == K_RIGHT:
					self.user_left_right = 0
					print("right")
				## ##
			elif event.type == VIDEORESIZE:
				global screen_size
				screen_size = event.size
				Screen.set_size(event.size)
			elif event.type == QUIT:
				exit()

		if self.manual_spawner:
			if Screen.get_mods() & KMOD_SHIFT:
				self.manual_spawner.intensity = SWARM_COUNT
			else:
				self.manual_spawner.intensity = 1

			self.manual_spawner.o_vel = [self.mouse_pos[0] - self.manual_spawner.pos[0], self.mouse_pos[1] - self.manual_spawner.pos[1]]
			self.manual_spawner.spawn()

		if self.text:
			if self.text_timeout > TEXT_TIMEOUT * FRAMERATE_VALUES[settings['framerate']]:
				self.text = ''
			else:
				self.text_timeout += 1

		self.display_data = {'holding': self.mouse_holding and not self.manual_spawner, 'init_pos': self.mouse_initial_pos, 'pos': self.mouse_pos, 'size': SIZE_VALUES[self.mass_selection], 'color': self.next_color, 'repulsor_mode': self.repulsor_mode, 'text': self.text}
		

	def add_object(self, isUser=0):
		velocity = (self.mouse_pos[0] - self.mouse_initial_pos[0], self.mouse_pos[1] - self.mouse_initial_pos[1])

		if self.mass_selection == 0:
			color = WHITE
		else:
			color = self.next_color
			self.next_color = (randint(0, 255), randint(0, 255), randint(0, 255))
		if self.repulsor_mode:
			mass = -MASS_VALUES[self.mass_selection]
		else:
			mass = MASS_VALUES[self.mass_selection]

		new_object = Object(self.mouse_initial_pos, velocity, color, mass)

		if isUser == 1:
			new_object.isUser=isUser
			print("add user says its a user")

		if self.mass_selection == 0:
			global minor_objects
			minor_objects.append(new_object)
		else:
			global major_objects
			major_objects.append(new_object)

		new_object.tick(major_objects)

	def add_spawner(self):
		global spawners
		velocity = (self.mouse_pos[0] - self.manual_spawner.pos[0], self.mouse_pos[1] - self.manual_spawner.pos[1])
		intensity = SWARM_COUNT if Screen.get_mods() & KMOD_SHIFT else 1	
		spawners.append(Spawner(self.manual_spawner.pos, velocity, intensity))

Screen = screen.Screen(SIZE_VALUES)
Clock = Clock()
InputHandler = InputHandler()
major_objects = []
minor_objects = []
spawners = []


while True:
	if not settings['paused']:
		for object in major_objects:
			object.tick(major_objects)
		for object in major_objects:
			object.update()
		for object in minor_objects:
			object.tick(major_objects)
		for spawner in spawners:
			spawner.spawn()
	InputHandler.handle_input(Screen)	
	Screen.frame(major_objects+minor_objects, InputHandler.display_data)
	Clock.tick(FRAMERATE_VALUES[settings['framerate']])	
