import pygame
from pygame.locals import *
from pygame import mixer
import pickle
import sys
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Get the directory where this script is located
current_dir = path.dirname(path.abspath(__file__))
img_dir = path.join(current_dir, 'img')

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 9
max_levels = 9
score = 0


#define colours
white = (255, 255, 255)
blue = (0, 0, 255)


#load images
sun_img = pygame.image.load(path.join(img_dir, 'sun.png'))
bg_img = pygame.image.load(path.join(img_dir, 'sky.png'))
restart_img = pygame.image.load(path.join(img_dir, 'restart_btn.png'))
start_img = pygame.image.load(path.join(img_dir, 'start_btn.png'))
exit_img = pygame.image.load(path.join(img_dir, 'exit_btn.png'))

#load sounds
pygame.mixer.music.load(path.join(img_dir, 'music.wav'))
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound(path.join(img_dir, 'img_coin.wav'))
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound(path.join(img_dir, 'img_jump.wav'))
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound(path.join(img_dir, 'game_over.wav'))
game_over_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


def load_level_data(level_number):
    try:
        bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        # First try the parent directory (where the level files are located)
        level_path = path.abspath(path.join(bundle_dir, '..', f'level{level_number}_data'))
        if not path.exists(level_path):
            # If not found, try the bundle directory itself
            level_path = path.join(bundle_dir, f'level{level_number}_data')
        if path.exists(level_path):
            with open(level_path, 'rb') as pickle_in:
                return pickle.load(pickle_in)
    except Exception as e:
        print(f"Error loading level {level_number}: {e}")
    return [[1] * 20 for _ in range(20)]  # Return a safe default level


#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	platform_group.empty()
	coin_group.empty()
	lava_group.empty()
	exit_group.empty()
	text_trigger_group.empty()
	win_group.empty()

	world_data = load_level_data(level)
	world = World(world_data)

	#create dummy coin for showing the score
	score_coin = Coin(tile_size // 2, tile_size // 2)
	coin_group.add(score_coin)
	return world


class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_a]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_d]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_a] == False and key[pygame.K_d] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1
				
			#check for collision with win sprite on the last level
			if level == max_levels and pygame.sprite.spritecollide(self, win_group, False):
				game_over = 2  # Special win condition
				draw_text('CONGRATULATIONS, YOU WIN!', font, blue, (screen_width // 2), screen_height // 2)


			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)

		return game_over


	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(path.join(img_dir, f'guy{num}.png'))
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load(path.join(img_dir, 'ghost.png'))
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



# Create sprite groups
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
text_trigger_group = pygame.sprite.Group()
win_group = pygame.sprite.Group()  # Add win group

# Define trigger messages dictionary
trigger_messages = {
    (1, 1): "Welcome to the game!",
    (5, 5): "Watch out for the lava!",
    (10, 10):"Collect all coins to proceed!",
	(15, 15):"These platforms move! Watch your step!",
	(20, 20):"Watch out for the enemies!",
	(25, 25):"They may look cute, but they're dangerous!",
	(30, 30):"Make sure not to fall!",
	(35, 35):"You got this!",
    # Add more messages with (x, y) coordinates as keys
}

class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load(path.join(img_dir, 'dirt.png'))
		grass_img = pygame.image.load(path.join(img_dir, 'grass.png'))

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				elif tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				elif tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				elif tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				elif tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				elif tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				elif tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				elif tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				elif tile == 9:
					trigger = TextTrigger(col_count * tile_size, row_count * tile_size)
					text_trigger_group.add(trigger)
				elif tile == 10:
					win = Win(col_count * tile_size, row_count * tile_size)
					win_group.add(win)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(path.join(img_dir, 'blob.png'))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(path.join(img_dir, 'platform.png'))
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1



class Win(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(path.join(img_dir, 'win.png'))
		self.image = pygame.transform.scale(img, (tile_size * 3, tile_size * 4))
		self.rect = self.image.get_rect()
		self.rect.x = x - tile_size  # Offset to center
		self.rect.y = y - tile_size * 2  # Offset upward to match editor placement
		
class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(path.join(img_dir, 'lava.png'))
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(path.join(img_dir, 'coin.png'))
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load(path.join(img_dir, 'exit.png'))
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

# Removing duplicate Win class definition


class TextTrigger(pygame.sprite.Sprite):
    # Messages organized by level
    level_messages = {
        1: [
            "Welcome to the game!",
            "Use WASD to move",
            "Press SPACE to jump"
        ],
        2: [
            "Watch out for the lava!"
        ],
        3: [
            "These platforms move!",
        ],
        4: [
            "Watch out for the enemies!, They may look cute, but they're dangerous!",
        ],
        5: [
            "The exit is juts up ahead",
        ],
        6: [
            "You're almost there!",
        ],
        7: [
            "This is a tricky one!",
        ],
        8: [
            "I hope you're having fun so far!",
        ],
		9: [
			"You're doing great!",
		],
		10: [
			"Time your jumps carefully!",
			"theres nothing here, why would you go here?",
		]
    }

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        # Store coordinates to preserve message assignment
        self.grid_x = x // tile_size
        self.grid_y = y // tile_size
        # Get level-specific messages or default ones
        current_level = level  # Using the global level variable
        level_specific_messages = TextTrigger.level_messages.get(current_level, ["Be careful!", "Keep going!", "You got this!"])
        # Assign message based on position in current level
        message_index = len([t for t in text_trigger_group if t.grid_x <= self.grid_x and t.grid_y <= self.grid_y])
        self.message = level_specific_messages[min(message_index, len(level_specific_messages) - 1)]
        self.active = False
        self.display_time = 0
        self.display_duration = 3500 

    def update(self):
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.display_time > self.display_duration:
                self.active = False

    def trigger(self):
        if not self.active:
            self.active = True
            self.display_time = pygame.time.get_ticks()

    def draw(self, screen):
        if self.active:
            # Get all active triggers and sort them by creation order
            active_triggers = [t for t in text_trigger_group if t.active]
            # Find our position in the active triggers list
            try:
                message_position = active_triggers.index(self)
            except ValueError:
                message_position = 0
              # Fixed x position in the middle of the screen
            x_pos = screen_width // 2
            # Stack messages vertically in the center of the screen
            padding = 40  # Space between messages
            base_y = screen_height // 2 - 100  # Starting Y position from center
            y_pos = base_y + (message_position * padding)
            
            # Render the text
            text_surf = font_score.render(self.message, True, blue)  # Changed color to blue
            text_rect = text_surf.get_rect(center=(x_pos, y_pos))
            screen.blit(text_surf, text_rect)


world_data = []

player = Player(100, screen_height - 130)

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

#load in level data and create world
try:
    bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
    level_path = path.abspath(path.join(bundle_dir, '..', f'level{level}_data'))
    if not path.exists(level_path):
        level_path = path.join(bundle_dir, f'level{level}_data')
    if path.exists(level_path):
        with open(level_path, 'rb') as pickle_in:
            world_data = pickle.load(pickle_in)
except Exception as e:
    print(f"Error loading level: {e}")
world = World(world_data)


#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))

	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)
			blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)
		win_group.draw(screen)  # Add win sprite group to be drawn

		# Update and draw text triggers
		text_trigger_group.update()
		# Check for collisions between player and triggers
		triggers_hit = pygame.sprite.spritecollide(player, text_trigger_group, False)
		for trigger in triggers_hit:
			trigger.trigger()
		
		# Draw any active trigger messages
		for trigger in text_trigger_group:
			trigger.draw(screen)

		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

		#if player has completed the level
		if game_over == 1:
			#reset game and go to next level
			level += 1
			if level <= max_levels:
				#reset level
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
				if restart_button.draw():
					level = 1
					#reset level
					world_data = []
					world = reset_level(level)
					game_over = 0
					score = 0

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()