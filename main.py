import screen
from pygame.time import Clock
from pygame.locals import *
from math import sqrt, atan2, sin, cos, pi, degrees
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
SWARM_MAX_VEL = 3
SWARM_COUNT = 10
SPAWNER_DELETE_DISTANCE = 25
TEXT_TIMEOUT = 4

USER_ACCELERATION_SPEED = 1000







class Object():
	def __init__(self, position, velocity, color=WHITE, mass=0):
		self.pos = list(position)
		self.vel = list(velocity)
		self.acl = [0,0]
		self.heading = 0
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


		## handeling of users using portals ##
		if self.isUser:
			for object in portal_objects:
				if object == self:
					continue
        
				distance = sqrt( ((self.pos[0] - object.pos[0])**2) + ((self.pos[1] - object.pos[1])**2))
				if distance < (self.size + object.size):
					object.traverse(self)
					break
		##  ##

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
		

		if self.isUser == 1:
		########self.vel[0] += InputHandler.user_left_right * timefactor
		########self.vel[1] += InputHandler.user_up_down * timefactor
		########print("vel is " + str(InputHandler.user_left_right) +", "+str(InputHandler.user_up_down))
			self.acl = [self.pos[0]-self.crosshairs.pos[0], self.pos[1]-self.crosshairs.pos[1]]

		self.vel[0] += (self.gravity[0] + self.acl[0]) * timefactor
		self.vel[1] += (self.gravity[1] + self.acl[1]) * timefactor
			

		
		self.pos[0] += self.vel[0] * timefactor
		self.pos[1] += self.vel[1] * timefactor

	def calculate_heading(self):
		x = self.vel[0]
		y = self.vel[1]
		self.heading = 180+degrees(atan2(x,y))




class Spawner(Object):
	def __init__(self, position, obj_velocity, velocity, intensity, color=WHITE, mass = 0, vel = 0):
		self.pos = list(position)
		self.vel = list(velocity)
		self.acl = [0,0]
		self.heading = 0
		self.color = color 
		self.mass = mass 
		self.size = 0.5 * pow(abs(mass), 1/3.0)	
		self.isUser = 0
		self.mass = mass
		self.o_vel = obj_velocity
		self.intensity = intensity
		self.spawn_counter = 0
		self.spinv=0
		


	def delete(self):
		global spawners, minor_objects
		spawners.remove(self)
		minor_objects.remove(self)

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

	def spin(self, speed):
		x = self.o_vel[0]
		y = self.o_vel[1]
		#theta = (180+(degrees(atan2(x,y))))
		print(x, y)
		self.o_vel[0] = cos(self.spinv)*100
		self.o_vel[1] = sin(self.spinv)*100 
		self.spinv+=(.01+90)
		print(self.o_vel[0],self.o_vel[1])


class GravityCrosshairs(Object):
	def __init__(self, user, colour = WHITE, mass = 0):
		self.isUser = 0
		self.pos = [0,0]
		self.vel = [0,0]
		self.acl = [0,0]
		self.color = color 
		self.mass = mass 
		self.size = 0.5 * pow(abs(mass), 1/3.0)	
		self.color = WHITE
		self.angle = 0
		self.user = user
		self.rotation_amount = 0

		global minor_objects
		crosshair_objects.append(self)

	def LockToUser(self):
		x = self.user.pos[0] + sin(self.angle) * 20
		y = self.user.pos[1] + cos(self.angle) * 20
		self.pos = [x,y]
		self.angle % pi
		print("crosshair angle is " + str(self.angle))

		self.angle += self.rotation_amount
		


class UserObject(Object):
	def __init__(self, position, velocity, colour = WHITE, mass = 3000):
		self.isUser = 1	
		self.pos = list(position)
		self.vel = list(velocity)
		self.acl = [0,0]
		self.color = color 
		self.mass = mass 
		self.size = 0.5 * pow(abs(mass), 1/3.0)	
		self.color = WHITE

		self.crosshairs = GravityCrosshairs(self)

	def delete(self):
		global user_objects
		if self in user_objects:
			user_objects.remove(self)

	def up(self):
		self.acl = 50
	def left(self):
		self.crosshairs.rotation_amount =.1
		self.crosshairs.LockToUser()

	def right(self):
		self.crosshairs.rotation_amount =-.1
		self.crosshairs.LockToUser()

	def space(self):
		print("tractor beam!")


########	OLD STEARING SCEME. MAY STILL HAVE USE.		###

########def up(self): 
########	print("user object says up!")
########        self.acl[1] = -USER_ACCELERATION_SPEED * timefactor
########def down(self):
########        self.acl[1] = USER_ACCELERATION_SPEED * timefactor
########def left(self):
########        self.acl[0] = -USER_ACCELERATION_SPEED * timefactor
########def right(self):
########        self.acl[0] = USER_ACCELERATION_SPEED * timefactor

	def release_up(self): 
		print("user object says up!")
	        self.acl[1] = 0#USER_ACCELERATION_SPEED * timefactor
	def release_down(self):
	        self.acl[1] = 0#USER_ACCELERATION_SPEED * timefactor
	def release_left(self):
	        self.crosshairs.rotation_amount = 0#USER_ACCELERATION_SPEED * timefactor
	def release_right(self):
	        self.crosshairs.rotation_amount = 0#USER_ACCELERATION_SPEED * timefactor






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
					user_objects[0].up()#self.user_up_down = -100
					print("up")
				elif event.key == K_DOWN:
					user_objects[0].down()#self.user_up_down = 100
					print("down")
				elif event.key == K_LEFT:
					user_objects[0].left()#self.user_left_right = -100
					print("left")
				elif event.key == K_RIGHT:
					user_objects[0].right()#self.user_left_right = 100
					print("right")
				elif event.key == K_SPACE:
					user_objects[0].space()
					print("space")
				#elif event.key == K_SPACE:
				## WARP ##
				elif event.key == K_w:
					self.warp("meh")
				## ##

			elif event.type == KEYUP:
				if event.key == K_s:
					self.manual_spawner = None
				## kill user keypress ##
				elif event.key == K_UP:
					user_objects[0].release_up()#self.user_up_down = -100
					print("up")
				elif event.key == K_DOWN:
					user_objects[0].release_down()#self.user_up_down = 100
					print("down")
				elif event.key == K_LEFT:
					user_objects[0].release_left()#self.user_left_right = -100
					print("left")
				elif event.key == K_RIGHT:
					user_objects[0].release_right()#self.user_left_right = 100
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


		if isUser == 1:
			new_object = UserObject(self.mouse_initial_pos, velocity, color, mass)
			new_object.isUser=isUser
			global user_objects
			user_objects.append(new_object)
			print("add user says its a user")
		else:
			new_object = Object(self.mouse_initial_pos, velocity, color, mass)

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

	def warp(self, destination, traveler):
		global major_objects, minor_objects, portal_objects, current_plane, user_objects, spawners
		new_traveler = traveler
		traveler.delete()
		cube_of_existance[current_plane].major_objects = major_objects
		cube_of_existance[current_plane].minor_objects = minor_objects
		cube_of_existance[current_plane].portal_objects = portal_objects
		cube_of_existance[current_plane].user_objects = user_objects
		cube_of_existance[current_plane].spawners = spawners
		for object in spawners:
			spawners.remove(object)

		target_plane = cube_of_existance[destination]
		new_traveler.vel = [-traveler.vel[0],-traveler.vel[1]]
		major_objects = target_plane.major_objects
		user_objects.append(new_traveler)

		minor_objects = target_plane.minor_objects
		portal_objects = target_plane.portal_objects
		spawners = target_plane.spawners
		current_plane = destination
		#print(current_plane)




class plane_of_existance():
	def __init__(self, major_objects, minor_objects, portal_objects, spawners = []):
		self.major_objects=major_objects
		self.minor_objects=minor_objects
		self.portal_objects=portal_objects
		self.spawners = spawners



class portal():
	def __init__(self, position, destination):
		self.mass = 1
		self.isUser = 0
		self.pos = position
		self.color = WHITE
		self.size = 50
		self.destination = destination

	def traverse(self, traveler):
		InputHandler.warp(self.destination, traveler)






Screen = screen.Screen(SIZE_VALUES)
Clock = Clock()
InputHandler = InputHandler()

current_plane = 0
cube_of_existance = []

major_objects = []
minor_objects = []
spawners = []

portal_objects = []
user_objects = []
crosshair_objects = []


while True:

	new_plane1 = plane_of_existance([],[],[])
	new_plane2 = plane_of_existance([],[],[portal([50,50],2)])
	new_plane3 = plane_of_existance([],[],[portal([250,50],0)])

	new_portal1 = portal([50,50],1)
	portal_objects.append(new_portal1)

	cube_of_existance.append(new_plane1)
	cube_of_existance.append(new_plane2)
	cube_of_existance.append(new_plane3)
	
	new_player = UserObject([300,300],[0,0])
	user_objects.append(new_player)

	new_spawner = Spawner([400,300],[0,0],[0,0],.3)
	minor_objects.append(new_spawner)


	break




while True:
	if not settings['paused']:
		for object in crosshair_objects:
			object.LockToUser()
			
		for object in user_objects:
			object.tick(major_objects+user_objects)
			object.calculate_heading()
		for object in major_objects:
			object.tick(major_objects+user_objects)
			object.calculate_heading()
		for object in user_objects:
			object.update()
		for object in major_objects:
			object.update()
		for object in minor_objects:
			try:
				object.o_vel
				new_spawner.spin(1)
				new_spawner.spawn()
			except AttributeError:
				"its not a spawner!"
			object.tick(major_objects+user_objects)
			object.calculate_heading()
		for spawner in spawners:
			spawner.spawn()
	InputHandler.handle_input(Screen)
	Screen.frame(major_objects+minor_objects+portal_objects+user_objects+crosshair_objects, InputHandler.display_data)
	Clock.tick(FRAMERATE_VALUES[settings['framerate']])	
