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
					#print("up")
				elif event.key == K_DOWN:
					user_objects[0].down()#self.user_up_down = 100
					#print("down")
				elif event.key == K_LEFT:
					user_objects[0].left()#self.user_left_right = -100
					#print("left")
				elif event.key == K_RIGHT:
					user_objects[0].right()#self.user_left_right = 100
					#print("right")
				elif event.key == K_SPACE:
					user_objects[0].space()
					#print("space")
				elif event.key == K_SPACE:
					add_mass_effect()
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
					#print("up")
				elif event.key == K_DOWN:
					user_objects[0].release_down()#self.user_up_down = 100
					#print("down")
				elif event.key == K_LEFT:
					user_objects[0].release_left()#self.user_left_right = -100
					#print("left")
				elif event.key == K_RIGHT:
					user_objects[0].release_right()#self.user_left_right = 100
					#print("right")
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


###	Looks like I should try to handel adding of all the objects here..		##

	# lets give it a try #
	def add_mass_effect(self):
		if IsUser:
			x,y = ScreenPos
			x2,y2 = user_objects[0].crosshairs.pos

			position = []
			position.append(x+2*(x-x2))
			position.append(y+2*(y-y2))

			new_mass_effect = MassEffect(position)
			
		


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
			new_object = UserObject(self.mouse_initial_pos, velocity, color, mass, kind = 'user')
			new_object.isUser=isUser
			global user_objects
			user_objects.append(new_object)
			#print("add user says its a user")
		else:
			new_object = Object(self.mouse_initial_pos, velocity, color, mass)

			if self.mass_selection == 0:
				self.kind = 'rock'
				global minor_objects
				minor_objects.append(new_object)
			else:
				global major_objects
				major_objects.append(new_object)
				self.kind = 'astroid'

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


