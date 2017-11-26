# Space Invaders
# Created by Lee Robinson

# !/usr/bin/env python
import math as mth
from pygame import *
import sys
import argparse
import numpy as np
from random import shuffle, randrange, choice, randint
from config import Config

#           R    G    B
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

SCREEN = display.set_mode((800, 600))
FONT = "fonts/space_invaders.ttf"
IMG_NAMES = ["ship", "ship", "mystery", "enemy1_1", "enemy1_2", "enemy2_1", "enemy2_2",
			 "enemy3_1", "enemy3_2", "explosionblue", "explosiongreen", "explosionpurple", "laser", "enemylaser"]
IMAGES = {name: image.load("images/{}.png".format(name)).convert_alpha()
		  for name in IMG_NAMES}


class Ship(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["ship"]
		self.rect = self.image.get_rect(topleft=(375, 540))
		self.speed = 5

	def update(self, keys, *args):
		if keys[K_LEFT] and self.rect.x > 10:
			self.rect.x -= self.speed
		if keys[K_RIGHT] and self.rect.x < 740:
			self.rect.x += self.speed
		game.screen.blit(self.image, self.rect)

	def move_left(self):
		if self.rect.x > 10:
			self.rect.x -= self.speed
		game.screen.blit(self.image, self.rect)

	def move_right(self):
		if self.rect.x < 740:
			self.rect.x += self.speed
		game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
	def __init__(self, xpos, ypos, direction, speed, filename, side):
		sprite.Sprite.__init__(self)
		self.image = IMAGES[filename]
		self.rect = self.image.get_rect(topleft=(xpos, ypos))
		self.speed = speed
		self.direction = direction
		self.side = side
		self.filename = filename

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)
		self.rect.y += self.speed * self.direction
		if self.rect.y < 15 or self.rect.y > 600:
			self.kill()


class Enemy(sprite.Sprite):
	def __init__(self, row, column):
		sprite.Sprite.__init__(self)
		self.row = row
		self.column = column
		self.images = []
		self.load_images()
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.direction = 1
		self.rightMoves = 15
		self.leftMoves = 30
		self.moveNumber = 0
		self.moveTime = 600
		self.firstTime = True
		self.movedY = False;
		self.columns = [False] * 10
		self.aliveColumns = [True] * 10
		self.addRightMoves = False
		self.addLeftMoves = False
		self.numOfRightMoves = 0
		self.numOfLeftMoves = 0
		self.timer = time.get_ticks()

	def update(self, keys, currentTime, killedRow, killedColumn, killedArray):
		self.check_column_deletion(killedRow, killedColumn, killedArray)
		if currentTime - self.timer > self.moveTime:
			self.movedY = False;
			if self.moveNumber >= self.rightMoves and self.direction == 1:
				self.direction *= -1
				self.moveNumber = 0
				self.rect.y += 35
				self.movedY = True
				if self.addRightMoves:
					self.rightMoves += self.numOfRightMoves
				if self.firstTime:
					self.rightMoves = self.leftMoves;
					self.firstTime = False;
				self.addRightMovesAfterDrop = False
			if self.moveNumber >= self.leftMoves and self.direction == -1:
				self.direction *= -1
				self.moveNumber = 0
				self.rect.y += 35
				self.movedY = True
				if self.addLeftMoves:
					self.leftMoves += self.numOfLeftMoves
				self.addLeftMovesAfterDrop = False
			if self.moveNumber < self.rightMoves and self.direction == 1 and not self.movedY:
				self.rect.x += 10
				self.moveNumber += 1
			if self.moveNumber < self.leftMoves and self.direction == -1 and not self.movedY:
				self.rect.x -= 10
				self.moveNumber += 1

			self.index += 1
			if self.index >= len(self.images):
				self.index = 0
			self.image = self.images[self.index]

			self.timer += self.moveTime
		game.screen.blit(self.image, self.rect)

	def check_column_deletion(self, killedRow, killedColumn, killedArray):
		if killedRow != -1 and killedColumn != -1:
			killedArray[killedRow][killedColumn] = 1
			for column in range(10):
				if all([killedArray[row][column] == 1 for row in range(5)]):
					self.columns[column] = True

		for i in range(5):
			if all([self.columns[x] for x in range(i + 1)]) and self.aliveColumns[i]:
				self.leftMoves += 5
				self.aliveColumns[i] = False
				if self.direction == -1:
					self.rightMoves += 5
				else:
					self.addRightMoves = True
					self.numOfRightMoves += 5

		for i in range(5):
			if all([self.columns[x] for x in range(9, 8 - i, -1)]) and self.aliveColumns[9 - i]:
				self.aliveColumns[9 - i] = False
				self.rightMoves += 5
				if self.direction == 1:
					self.leftMoves += 5
				else:
					self.addLeftMoves = True
					self.numOfLeftMoves += 5

	def load_images(self):
		images = {0: ["1_2", "1_1"],
				  1: ["2_2", "2_1"],
				  2: ["2_2", "2_1"],
				  3: ["3_1", "3_2"],
				  4: ["3_1", "3_2"],
				  }
		img1, img2 = (IMAGES["enemy{}".format(img_num)] for img_num in images[self.row])
		self.images.append(transform.scale(img1, (40, 35)))
		self.images.append(transform.scale(img2, (40, 35)))


class Blocker(sprite.Sprite):
	def __init__(self, size, color, row, column):
		sprite.Sprite.__init__(self)
		self.height = size
		self.width = size
		self.color = color
		self.image = Surface((self.width, self.height))
		self.image.fill(self.color)
		self.rect = self.image.get_rect()
		self.row = row
		self.column = column

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)


# noinspection PyRedundantParentheses,PyRedundantParentheses
class Mystery(sprite.Sprite):
	def __init__(self):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["mystery"]
		self.image = transform.scale(self.image, (75, 35))
		self.rect = self.image.get_rect(topleft=(-80, 45))
		self.row = 5
		self.moveTime = 25000
		self.direction = 1
		self.timer = time.get_ticks()
		self.mysteryEntered = mixer.Sound('sounds/mysteryentered.wav')
		self.mysteryEntered.set_volume(0.3)
		self.playSound = True

	def update(self, keys, currentTime, *args):
		resetTimer = False
		if (currentTime - self.timer > self.moveTime) and (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
			self.mysteryEntered.play()
			self.playSound = False
		if (currentTime - self.timer > self.moveTime) and self.rect.x < 840 and self.direction == 1:
			self.mysteryEntered.fadeout(4000)
			self.rect.x += 2
			game.screen.blit(self.image, self.rect)
		if (currentTime - self.timer > self.moveTime) and self.rect.x > -100 and self.direction == -1:
			self.mysteryEntered.fadeout(4000)
			self.rect.x -= 2
			game.screen.blit(self.image, self.rect)
		if (self.rect.x > 830):
			self.playSound = True
			self.direction = -1
			resetTimer = True
		if (self.rect.x < -90):
			self.playSound = True
			self.direction = 1
			resetTimer = True
		if (currentTime - self.timer > self.moveTime) and resetTimer:
			self.timer = currentTime


class Explosion(sprite.Sprite):
	def __init__(self, xpos, ypos, row, ship, mystery, score):
		sprite.Sprite.__init__(self)
		self.isMystery = mystery
		self.isShip = ship
		if mystery:
			self.text = Text(FONT, 20, str(score), WHITE, xpos + 20, ypos + 6)
		elif ship:
			self.image = IMAGES["ship"]
			self.rect = self.image.get_rect(topleft=(xpos, ypos))
		else:
			self.row = row
			self.load_image()
			self.image = transform.scale(self.image, (40, 35))
			self.rect = self.image.get_rect(topleft=(xpos, ypos))
			game.screen.blit(self.image, self.rect)

		self.timer = time.get_ticks()

	def update(self, keys, currentTime):
		if self.isMystery:
			if currentTime - self.timer <= 200:
				self.text.draw(game.screen)
			if currentTime - self.timer > 400 and currentTime - self.timer <= 600:
				self.text.draw(game.screen)
			if currentTime - self.timer > 600:
				self.kill()
		elif self.isShip:
			if currentTime - self.timer > 300 and currentTime - self.timer <= 600:
				game.screen.blit(self.image, self.rect)
			if currentTime - self.timer > 900:
				self.kill()
		else:
			if currentTime - self.timer <= 100:
				game.screen.blit(self.image, self.rect)
			if currentTime - self.timer > 100 and currentTime - self.timer <= 200:
				self.image = transform.scale(self.image, (50, 45))
				game.screen.blit(self.image, (self.rect.x - 6, self.rect.y - 6))
			if currentTime - self.timer > 400:
				self.kill()

	def load_image(self):
		imgColors = ["purple", "blue", "blue", "green", "green"]
		self.image = IMAGES["explosion{}".format(imgColors[self.row])]


class Life(sprite.Sprite):
	def __init__(self, xpos, ypos):
		sprite.Sprite.__init__(self)
		self.image = IMAGES["ship"]
		self.image = transform.scale(self.image, (23, 23))
		self.rect = self.image.get_rect(topleft=(xpos, ypos))

	def update(self, keys, *args):
		game.screen.blit(self.image, self.rect)


class Text(object):
	def __init__(self, textFont, size, message, color, xpos, ypos):
		self.font = font.Font(textFont, size)
		self.surface = self.font.render(message, True, color)
		self.rect = self.surface.get_rect(topleft=(xpos, ypos))

	def draw(self, surface):
		surface.blit(self.surface, self.rect)


# noinspection PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses,PyRedundantParentheses
class SpaceInvaders(object):
	def __init__(self):
		mixer.pre_init(44100, -16, 1, 512)
		init()
		self.caption = display.set_caption('Space Invaders')
		self.screen = SCREEN
		self.background = image.load('images/background.jpg').convert()
		self.startGame = False
		self.mainScreen = True
		self.gameOver = False
		# Initial value for a new game
		self.enemyPositionDefault = 65
		# Counter for enemy starting position (increased each new round)
		self.enemyPositionStart = self.enemyPositionDefault
		# Current enemy starting position
		self.enemyPosition = self.enemyPositionStart

		# STORE Enemy sprite locations -- update each time get_state is updated.
		self.enemySpritesArray = []  # TODO: fix -- working on

	def reset(self, score, lives, newGame=False):
		self.player = Ship()
		self.playerGroup = sprite.Group(self.player)
		self.explosionsGroup = sprite.Group()
		self.bullets = sprite.Group()
		self.mysteryShip = Mystery()
		self.mysteryGroup = sprite.Group(self.mysteryShip)
		self.enemyBullets = sprite.Group()
		self.reset_lives(lives)
		self.enemyPosition = self.enemyPositionStart
		self.make_enemies()
		# Only create blockers on a new game, not a new round
		if newGame:
			self.allBlockers = sprite.Group(self.make_blockers(0), self.make_blockers(1), self.make_blockers(2),
											self.make_blockers(3))
		self.keys = key.get_pressed()
		self.clock = time.Clock()
		self.timer = time.get_ticks()
		self.noteTimer = time.get_ticks()
		self.shipTimer = time.get_ticks()
		self.score = score
		self.lives = lives
		self.create_audio()
		self.create_text()
		self.killedRow = -1
		self.killedColumn = -1
		self.makeNewShip = False
		self.shipAlive = True
		self.killedArray = [[0] * 10 for x in range(5)]

	def make_blockers(self, number):
		blockerGroup = sprite.Group()
		for row in range(4):
			for column in range(9):
				blocker = Blocker(10, GREEN, row, column)
				blocker.rect.x = 50 + (200 * number) + (column * blocker.width)
				blocker.rect.y = 450 + (row * blocker.height)
				blockerGroup.add(blocker)
		return blockerGroup

	def reset_lives_sprites(self):
		self.life1 = Life(715, 3)
		self.life2 = Life(742, 3)
		self.life3 = Life(769, 3)

		if self.lives == 3:
			self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)
		elif self.lives == 2:
			self.livesGroup = sprite.Group(self.life1, self.life2)
		elif self.lives == 1:
			self.livesGroup = sprite.Group(self.life1)

	def reset_lives(self, lives):
		self.lives = lives
		self.reset_lives_sprites()

	def create_audio(self):
		self.sounds = {}
		for sound_name in ["shoot", "shoot2", "invaderkilled", "mysterykilled", "shipexplosion"]:
			self.sounds[sound_name] = mixer.Sound("sounds/{}.wav".format(sound_name))
			self.sounds[sound_name].set_volume(0.2)

		self.musicNotes = [mixer.Sound("sounds/{}.wav".format(i)) for i in range(4)]
		for sound in self.musicNotes:
			sound.set_volume(0.5)

		self.noteIndex = 0

	def play_main_music(self, currentTime):
		moveTime = self.enemies.sprites()[0].moveTime
		if currentTime - self.noteTimer > moveTime:
			self.note = self.musicNotes[self.noteIndex]
			if self.noteIndex < 3:
				self.noteIndex += 1
			else:
				self.noteIndex = 0

			self.note.play()
			self.noteTimer += moveTime

	def create_text(self):
		self.titleText = Text(FONT, 50, "Space Invaders", WHITE, 164, 155)
		self.titleText2 = Text(FONT, 25, "Press any key to continue", WHITE, 201, 225)
		self.gameOverText = Text(FONT, 50, "Game Over", WHITE, 250, 270)
		self.nextRoundText = Text(FONT, 50, "Next Round", WHITE, 240, 270)
		self.enemy1Text = Text(FONT, 25, "   =   10 pts", GREEN, 368, 270)
		self.enemy2Text = Text(FONT, 25, "   =  20 pts", BLUE, 368, 320)
		self.enemy3Text = Text(FONT, 25, "   =  30 pts", PURPLE, 368, 370)
		self.enemy4Text = Text(FONT, 25, "   =  ?????", RED, 368, 420)
		self.scoreText = Text(FONT, 20, "Score", WHITE, 5, 5)
		self.livesText = Text(FONT, 20, "Lives ", WHITE, 640, 5)

	def check_input(self):
		self.keys = key.get_pressed()
		for e in event.get():
			if e.type == QUIT:
				sys.exit()
			if e.type == KEYDOWN:
				if e.key == K_SPACE:
					if len(self.bullets) == 0 and self.shipAlive:
						if self.score < 1000:
							bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, "laser", "center")
							self.bullets.add(bullet)
							self.allSprites.add(self.bullets)
							self.sounds["shoot"].play()
						else:
							leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, "laser", "left")
							rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, "laser",
												 "right")
							self.bullets.add(leftbullet)
							self.bullets.add(rightbullet)
							self.allSprites.add(self.bullets)
							self.sounds["shoot2"].play()

	# check if enemy to left
	def enemy_bullet_is_left(self, proximityStates, shipX, shipY):
		if shipY > 0:
			if proximityStates[shipX - 4][shipY - 1] == 3 or proximityStates[shipX - 3][shipY - 1] == 3 or \
							proximityStates[shipX - 2][shipY - 1] == 3 or proximityStates[shipX - 1][shipY - 1] == 3:
				return True
		return False

	# checks the row above the enemy and checks to see if a bullet is within x coordinates of the ship -- this allows us to give enough time to move
	def enemey_bullet_is_right(self, proximityStates, shipX, shipY):
		if shipY < 23:
			if proximityStates[shipX - 4][shipY + 1] == 3 or proximityStates[shipX - 3][shipY + 1] == 3 or \
							proximityStates[shipX - 2][shipY + 1] == 3 or proximityStates[shipX - 1][shipY + 1] == 3:
				return True
		return False

	# player ship is divided into six sections spread across six rows. This method takes a ship row and checks to see if a bullet is coming towards that part of the ship.
	# if no bullets are found, a value of 10,000 is returned to indicate that no bullets are present
	# otherwise, it will return the col# the bullet is in, a higher #  returned indicates a higher threat to the ship because it means the bullet is closest to it.
	def findClosetBullet(self, rowToSearch):
		print("calling find closestBUllet: ", rowToSearch)  # TODO: remove after testing
		for i in range((len(rowToSearch) - 1), 0,
					   -1):  # Starts searching for bullet from col 9 to zero, returning the index of the bullet closest to the ship.
			if rowToSearch[i] == 5:
				break
			if rowToSearch[i] == 3:
				return i
		return Config.inf

	# returns the index representing the part of ship vulnerable that has the closet bullets
	def highestPriorityBullet(self, bulletArray):
		# pos = "none"
		pos = []
		highestvalue = -99  # place holder    --- TODO: what if multiple places have bullets in same position?
		for i in range(0, len(bulletArray) - 1):  # dont want to include col row is in
			if bulletArray[i] != Config.inf and bulletArray[i] >= highestvalue:
				highestvalue = bulletArray[i]
				pos.append(
					i)  # bullet array has length six - 1 position for each of the rows used to reprsent the ship. if 4 is in the list, it means that the ships center is the most vulnerable part of the ship.

		# no bullets approaching any parts of the ship
		if len(pos) == 0:
			return "none"

		# two or more parts of the ship are equally vulnerable to being hit by an enemy bullet  -- TODO: create logic to determine which part of the ship should be prioritized -- might want to check nearby rows to help make decision
		if len(pos) > 1:
			return 4  # placeholder - prioritze ship rcenter
		# TODO: add logic to figure out which bullet to prioritize
		return pos

	# TODO: rather then
	# check if enemies are x rows above- or x rows below -- if so -- check if within shooting distance -- if  not - move towards it.
	def playerAndEnemyPolicy(self, stateArray):

		enemysAbove = False
		enemysBelow = True

		shipCenterRow = self.player.rect.center[0]


		print("test of enemeyArray", self.enemySpritesArray)
		# for enemy in self.enemySpritesArray:
		# 	print("enemy location: ", enemy.rect)
		#

	# get enemy ships sprites: find location

	# check if any are within x positions heading towards the ship  -- if so return 0

	# if ships are moving away from the ship


	# #if enemy is 10 rows above ship and is moving in the direction of the ship
	# for row in range(0, shipCenterRow):
	# 	if stateArray[row] == 2:
	# 		if sta
	#
	# #checking if enemies are below ship
	# for row in range(shipCenterRow, 80):
	# 	if stateArray[row] == 2:


	# enemysAbove = True

	# if enemy is 10 rows below ship



	##Strategy: prioritize dodging or killing bullets within 3 * 50 px of any part of the ship
	## otherwise shoot and hope target is hit -- next iteration will try to be strategic about hitting enemies.
	## action map:
	#            shoot: 0
	#            move left: 1
	#            move right: 2
	@property
	def utility(self):

		bulletFound = False

		shipCenterRow = mth.floor(self.player.rect.center[0] / Config.heightFactor) - 1  # row?
		shipCenterCol = mth.floor(self.player.rect.center[1] / Config.widthFactor) - 1

		text = Text(FONT, 20, str("Ship Coord - col: ") + str(shipCenterRow) + ',row:' + str(shipCenterCol), GREEN, 135,
					5)  # TODO: remove? I think its fun to see the ships current location.
		text.draw(self.screen)

		##Get state spaces
		stateArray = self.get_state()
		self.playerAndEnemyPolicy(stateArray)

		# TODO: make constant
		# array that holds position of bullet for each vulnerability on ship . To determine which action to prioritize depending on which bullet is closer    - [leftTip][leftCenter][center][rightRight][rightTip]
		enemyBulletsPositions = [Config.inf for x in range(7)]

		# bullet is approching very edge of left wing tip
		leftWingTipEdge = stateArray[(shipCenterRow - 3), :]
		if leftWingTipEdge.__contains__(3):
			enemyBulletsPositions[0] = self.findClosetBullet(leftWingTipEdge)

		# enemy bullet is about to hit the tip of the ship's left wing -- move ship right to dodge
		leftWingTip = stateArray[(shipCenterRow - 2), :]
		if leftWingTip.__contains__(3):
			enemyBulletsPositions[0] = self.findClosetBullet(leftWingTip)

		# bullet heading towards left wing - move ship left to center ship with enemy bullet and counter bullet next round
		leftWingCen = stateArray[shipCenterRow - 1, :]
		if leftWingCen.__contains__(3):
			enemyBulletsPositions[1] = self.findClosetBullet(leftWingCen)

		# bullet approaching center of ship -- counter bullet and hope other enemy bullets don't hit other parts of the ship
		colCenter = stateArray[shipCenterRow, :]
		if colCenter.__contains__(3):
			enemyBulletsPositions[2] = self.findClosetBullet(colCenter)

		# bullet is approaching right wing -- move ship right to counter bullet next round
		rightWingCen = stateArray[shipCenterRow + 1, :]
		if rightWingCen.__contains__(3):
			enemyBulletsPositions[3] = self.findClosetBullet(rightWingCen)

		# bullet is approaching tip of the ship's right wing -- move ship left to dodge
		rightWingTip = stateArray[shipCenterRow + 2, :]
		if rightWingTip.__contains__(3):
			enemyBulletsPositions[4] = self.findClosetBullet(rightWingTip)

		# TODO: keep?
		rightWingTipTip = stateArray[shipCenterRow + 3, :]
		if rightWingTipTip.__contains__(3):
			enemyBulletsPositions[5] = self.findClosetBullet(rightWingTipTip)

		print(leftWingTipEdge)
		print(leftWingTip)  ##TODO: remove after testing
		print(leftWingCen)
		print(colCenter)  # TODO: remove after testing
		print(rightWingCen)
		print(rightWingTip)

		print("enemy bullet positions", enemyBulletsPositions)
		# find highest prority


		# TODO: combine if logic
		# returns an empty array if no bullets are coming towards ship
		highestPriority = self.highestPriorityBullet(enemyBulletsPositions)
		print("highestPrioirty bullet: ", highestPriority)
		if highestPriority != "none":
			if highestPriority == 0:  # bullet is approching very edge of left wing tip  --- move ship right to dodge - provided this does not move in line of bullet
				if (shipCenterRow - 3) > 0 and stateArray[shipCenterRow - 4][shipCenterCol] != 3 and stateArray[shipCenterRow - 4][shipCenterCol - 1] != 3:  # TODO: maybe check if col -2 and col - 3 also -- if we move right, we want to make sure we have plenty of time to get out of the way
					return 2  # move rightWingTip
				return 1  # move ship left and hope that we have enough time to counter by moving left - - probably doomed
			elif highestPriority == 1:  # bullet is
				return 2  # TODO: add logic
			elif highestPriority == 2:  # bullet approaching the right of center of the left ship wing --  move ship left to counter bullet next term and hope other enemy bullets don't hit other parts of the ship
				return 1
			elif highestPriority == 0:  # bullet approaching center of ship -- counter bullet and hope other enemy bullets don't hit other parts of the ship
				return 0  # TODO: add logic
			elif highestPriority == 4:  # bullet is approaching right wing -- move ship left to counter bullet next round
				return 1  # TODO: add logic
			elif highestPriority == 5:  #
				return 2  # TODO: comback  - add logic
			else:  # bullet is approaching tip of the ship's right wing -- move ship left to dodge
				if (shipCenterRow - 2) > 1 and stateArray[shipCenterRow + 3][shipCenterCol] != 3:  # TODO right wing high row # count means further right on screen -- move left means minus 1 to row
					return 1
				return 2;  # Can't move right -- because it either moves the ship into a bullet, or there is not enough room to move right.
		else:
			# print("if ")
			# TODO: check if enemy within range of guns bullet in next 10 rounds -- if not, move in directions that puts ships in prox with bullet

			return 0  # TODO add better logic
		# if pos returned has



		# if rightWingCen[shipCenterCol - 3] == 3 or rightWingCen[
		# 			shipCenterCol - 2] == 3:  # colLeft[shipCenterCol - 1] does not leave enough time to counter bullet, no hope left :(

		#	if leftWingTip[shipCenterCol - 3] == 3 or leftWingTip[shipCenterCol - 2] == 3 or leftWingTip[ shipCenterCol - 1] == 3:
		#	return 2  # move right to dodge if no enemy

		# if leftWingCen[shipCenterCol - 2] == 3 or leftWingCen[
		# 			shipCenterCol - 2] == 3:  # colLeft[shipCenterCol - 1] does not leave enough time to counter bullet, no hope left


		# address the bullet closet to

		# if rightWingTip[shipCenterCol - 2] == 3 or rightWingTip[
		# 			shipCenterCol - 2] == 3:  # colRightRight[shipCenterCol - 1] does not leave enough time to counter bullet, no hope left :(
		#	return 1;  # move ship left to dodge

		# return 2  # move right to counter next round







		# if no bullets to worry about -- pick best move, if enemy nearby -- and coming direction of ship -- shoot, else move

		# shoot in every other situation
		return 0;

		# noinspection PyPep8
		#  #if bullet is the directly above us, check left and right and move to best position to continue to
		#  if proximityStates[shipX-3][shipY] == 3 or proximityStates[shipX-2][shipY] == 3 or proximityStates[shipX-1][shipY] == 3:
		#
		#     # if self.enemey_bullet_is_right(proximityStates, shipX, shipY):
		#     #      return 1  #move left
		#     #  if self.enemy_bullet_is_left(proximityStates, shipX, shipY):
		#     #      return 2  #move right
		#      return 0    #dodging puts as in equally bad state. shoot and hope we kill the bullet in time.
		#
		#  #No bullets are in the same row as us but we need check to see if the row above or below us contains bullets because it will kill us  -- side effect of how we represented state space.
		# #this is because bullets are 1/3 of size of ship. can adjust this if we converted the array to be n * the width of the
		#  if self.enemey_bullet_is_right(proximityStates, shipX, shipY):
		#      return 1  # move left
		#
		#  if self.enemy_bullet_is_left(proximityStates, shipX, shipY):
		#      return 2  # move right

		return 0  # no need to dodge, shoot and hope we hit an invader.

	# add logic to check if enemy is in row above and if not, shoot and move? shooting enemies if chance

	#
	#     print("first conditiaional ship to Right:", proximityStates[shipX-1][shipY-1], "row:", proximityStates[shipY-1,:])
	#
	#     if proximityStates[shipX-1][shipY-1] == 3:
	#         print("bullet will hit left side of ship. move right? grabbing row: ", proximityStates[shipY-1,:])
	#         return 2
	#
	# if shipX > 0 and shipY < 23:
	#     print("first conditiaional ship to left:", proximityStates[shipX-1][shipY-1])
	#     if proximityStates[shipX-1][shipY+1] == 3:
	#         print("bullet will hit right side of ship. move left? grabbing row: ", proximityStates[shipY-1,:])
	#         return 1
	#
	# return 0;
	# if proximityStates[shipX-1][shipY-1] == 1:
	#     print("bullet will hit left side of ship. move right? grabbing row: ", proximityStates[shipY-1,:])
	#     return 2

	# if bullet in same row as ship, row to the left, or right to the right --- get out of dodge, enemy bullet will kill you. move left or move right.


	##TODO: if bullet in ships vision -- move left or right depending on which has higher potential to get score.


	##expand to get list that contains ship coords and array of nearyby sprites gride
	def get_action(self):
		print("ship x original ", self.player.rect.center[0])
		print("size of ship ", self.player.rect)

		self.keys = key.get_pressed()
		for e in event.get():
			if e.type == QUIT:
				sys.exit()

		# action = 0
		action = self.utility

		# randint(0, 2)
		if (action == 0):
			self.shoot()
		if (action == 1):
			self.player.move_left()
		if (action == 2):
			self.player.move_right()

	def get_genetic_action(self):
		self.keys = key.get_pressed()
		for e in event.get():
			if e.type == QUIT:
				sys.exit()

	def shoot(self):
		if len(self.bullets) == 0 and self.shipAlive:
			if self.score < 1000:
				bullet = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, -1, 15, "laser", "center")
				self.bullets.add(bullet)
				self.allSprites.add(self.bullets)
				self.sounds["shoot"].play()
			else:
				leftbullet = Bullet(self.player.rect.x + 8, self.player.rect.y + 5, -1, 15, "laser", "left")
				rightbullet = Bullet(self.player.rect.x + 38, self.player.rect.y + 5, -1, 15, "laser", "right")
				self.bullets.add(leftbullet)
				self.bullets.add(rightbullet)
				self.allSprites.add(self.bullets)
				self.sounds["shoot2"].play()

	def make_enemies(self):
		enemies = sprite.Group()
		for row in range(5):
			for column in range(10):
				enemy = Enemy(row, column)
				enemy.rect.x = 157 + (column * 50)
				enemy.rect.y = self.enemyPosition + (row * 45)
				enemies.add(enemy)

		self.enemies = enemies
		self.allSprites = sprite.Group(self.player, self.enemies, self.livesGroup, self.mysteryShip)

	def make_enemies_shoot(self):
		columnList = []
		for enemy in self.enemies:
			columnList.append(enemy.column)

		columnSet = set(columnList)
		columnList = list(columnSet)
		shuffle(columnList)
		column = columnList[0]
		enemyList = []
		rowList = []

		for enemy in self.enemies:
			if enemy.column == column:
				rowList.append(enemy.row)
		row = max(rowList)
		for enemy in self.enemies:
			if enemy.column == column and enemy.row == row:
				if (time.get_ticks() - self.timer) > 200:  # changed from original 700 (affects enemy bullet amount)
					self.enemyBullets.add(Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5, "enemylaser", "center"))
					self.allSprites.add(self.enemyBullets)
					self.timer = time.get_ticks()

	def calculate_score(self, row):
		scores = {0: 30,
				  1: 20,
				  2: 20,
				  3: 10,
				  4: 10,
				  5: choice([50, 100, 150, 300])
				  }

		score = scores[row]
		self.score += score
		return score

	# ship size      50, 48          <width, height>
	# enemy ship size 40,35
	# ship bullet sprite size:  <rect(398, 515, 5, 15)>
	#
	# TODO: either make a copy or ask permision to change if this works
	def get_state(self):
		height = mth.floor(800 / Config.heightFactor)  # 800 /10 = 80 rows
		width = mth.floor(600 / Config.widthFactor)  # 600 / 50 = 12 columns
		state_array = np.zeros([height, width], dtype=np.int)
		for spr in self.allSprites.sprites():
			row = mth.floor(spr.rect.center[0] / Config.heightFactor) - 1
			col = mth.floor(spr.rect.center[1] / Config.widthFactor) - 1
			if type(spr).__name__ == 'Ship':
				state_array[row + 2][col] = 1  # keep
				state_array[row + 1][col] = 1
				state_array[row][col] = 1
				state_array[row - 1][col] = 1
				state_array[row - 2][col] = 1
				state_array[row - 3][col] = 1  # keep for sure -- do not even think about deleting

			if type(spr).__name__ == 'Enemy':
				self.enemySpritesArray.append(spr)
				#TODO: add  conditional check
				state_array[row - 2][col] = 2
				state_array[row - 1][col] = 2
				state_array[row][col] = 2
				state_array[row + 1][col] = 2
			if type(spr).__name__ == 'Bullet':
				if (spr.direction == 1):
					state_array[row][col] = 3
				else:
					state_array[row][col] = 6
			if type(spr).__name__ == 'Mystery':
				if row >= 0 and col >= 0 and row < height and col <= width:
					state_array[row - 3][col] = 4
					state_array[row - 2][col] = 4
					state_array[row - 1][col] = 4
					if (row < 79):
						state_array[row + 1][col] = 4
					if (row < 78):
						state_array[row + 2][col] = 4
					if (row < 77):
						state_array[row + 3][col] = 4

		for blocker in self.allBlockers:
			row = mth.floor(blocker.rect.center[0] / Config.heightFactor) - 1
			col = mth.floor(blocker.rect.center[1] / Config.widthFactor) - 1
			state_array[row][col] = 5
		# TODO: put back in if desired?
		# np.savetxt('state.txt', state_array, fmt='%i')
		print(state_array)
		# print(state_array)

		return state_array  # TODO: remove transpose after testing

	def create_main_menu(self):
		self.enemy1 = IMAGES["enemy3_1"]
		self.enemy1 = transform.scale(self.enemy1, (40, 40))
		self.enemy2 = IMAGES["enemy2_2"]
		self.enemy2 = transform.scale(self.enemy2, (40, 40))
		self.enemy3 = IMAGES["enemy1_2"]
		self.enemy3 = transform.scale(self.enemy3, (40, 40))
		self.enemy4 = IMAGES["mystery"]
		self.enemy4 = transform.scale(self.enemy4, (80, 40))
		self.screen.blit(self.enemy1, (318, 270))
		self.screen.blit(self.enemy2, (318, 320))
		self.screen.blit(self.enemy3, (318, 370))
		self.screen.blit(self.enemy4, (299, 420))

		for e in event.get():
			if e.type == QUIT:
				sys.exit()
			if e.type == KEYUP:
				self.startGame = True
				self.mainScreen = False

	def update_enemy_speed(self):
		if len(self.enemies) <= 10:
			for enemy in self.enemies:
				enemy.moveTime = 400
		if len(self.enemies) == 1:
			for enemy in self.enemies:
				enemy.moveTime = 200

	def check_collisions(self):
		print("Checking colliion -- not indicative of a real collision")
		self.get_state()
		collidedict = sprite.groupcollide(self.bullets, self.enemyBullets, True, False)
		if collidedict:
			for value in collidedict.values():
				for currentSprite in value:
					self.enemyBullets.remove(currentSprite)
					self.allSprites.remove(currentSprite)

		enemiesdict = sprite.groupcollide(self.bullets, self.enemies, True, False)
		if enemiesdict:
			for value in enemiesdict.values():
				for currentSprite in value:
					self.sounds["invaderkilled"].play()
					self.killedRow = currentSprite.row
					self.killedColumn = currentSprite.column
					score = self.calculate_score(currentSprite.row)
					explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, False,
										  score)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(currentSprite)
					self.enemies.remove(currentSprite)
					self.gameTimer = time.get_ticks()
					break

		mysterydict = sprite.groupcollide(self.bullets, self.mysteryGroup, True, True)
		if mysterydict:
			for value in mysterydict.values():
				for currentSprite in value:
					currentSprite.mysteryEntered.stop()
					self.sounds["mysterykilled"].play()
					score = self.calculate_score(currentSprite.row)
					explosion = Explosion(currentSprite.rect.x, currentSprite.rect.y, currentSprite.row, False, True,
										  score)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(currentSprite)
					self.mysteryGroup.remove(currentSprite)
					newShip = Mystery()
					self.allSprites.add(newShip)
					self.mysteryGroup.add(newShip)
					break

		bulletsdict = sprite.groupcollide(self.enemyBullets, self.playerGroup, True, False)
		if bulletsdict:
			for value in bulletsdict.values():
				for playerShip in value:
					# TODO: remove after testing
					print("\n\n collision!")
					self.get_state()
					if self.lives == 3:
						self.lives -= 1
						self.livesGroup.remove(self.life3)
						self.allSprites.remove(self.life3)
					elif self.lives == 2:
						self.lives -= 1
						self.livesGroup.remove(self.life2)
						self.allSprites.remove(self.life2)
					elif self.lives == 1:
						self.lives -= 1
						self.livesGroup.remove(self.life1)
						self.allSprites.remove(self.life1)
						self.gameOver = True
						self.startGame = False

					self.sounds["shipexplosion"].play()
					explosion = Explosion(playerShip.rect.x, playerShip.rect.y, 0, True, False, 0)
					self.explosionsGroup.add(explosion)
					self.allSprites.remove(playerShip)
					self.playerGroup.remove(playerShip)
					self.makeNewShip = True
					self.shipTimer = time.get_ticks()
					self.shipAlive = False

		if sprite.groupcollide(self.enemies, self.playerGroup, True, True):
			self.gameOver = True
			self.startGame = False

		sprite.groupcollide(self.bullets, self.allBlockers, True, True)
		sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
		sprite.groupcollide(self.enemies, self.allBlockers, False, True)

	def create_new_ship(self, createShip, currentTime):
		if createShip and (currentTime - self.shipTimer > 900):
			self.player = Ship()
			self.allSprites.add(self.player)
			self.playerGroup.add(self.player)
			self.makeNewShip = False
			self.shipAlive = True

	def create_game_over(self, currentTime):
		self.screen.blit(self.background, (0, 0))
		if currentTime - self.timer < 750:
			self.gameOverText.draw(self.screen)
		if currentTime - self.timer > 750 and currentTime - self.timer < 1500:
			self.screen.blit(self.background, (0, 0))
		if currentTime - self.timer > 1500 and currentTime - self.timer < 2250:
			self.gameOverText.draw(self.screen)
		if currentTime - self.timer > 2250 and currentTime - self.timer < 2750:
			self.screen.blit(self.background, (0, 0))
		if currentTime - self.timer > 3000:
			self.mainScreen = True

		for e in event.get():
			if e.type == QUIT:
				sys.exit()

	def main(self, it):
		i = 0
		scoreList = set()
		while True:
			if self.mainScreen:
				i += 1
				self.reset(0, 1, True)
				self.screen.blit(self.background, (0, 0))
				self.titleText.draw(self.screen)
				self.titleText2.draw(self.screen)
				self.enemy1Text.draw(self.screen)
				self.enemy2Text.draw(self.screen)
				self.enemy3Text.draw(self.screen)
				self.enemy4Text.draw(self.screen)
				self.create_main_menu()
				self.startGame = True
				self.mainScreen = False

			elif self.startGame:
				if len(self.enemies) == 0:
					currentTime = time.get_ticks()
					if currentTime - self.gameTimer < 3000:
						self.screen.blit(self.background, (0, 0))
						self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
						self.scoreText.draw(self.screen)
						self.scoreText2.draw(self.screen)
						self.nextRoundText.draw(self.screen)
						self.livesText.draw(self.screen)
						self.livesGroup.update(self.keys)
						self.get_action()
					if currentTime - self.gameTimer > 3000:
						# Move enemies closer to bottom
						self.enemyPositionStart += 35
						self.reset(self.score, self.lives)
						self.make_enemies()
						self.gameTimer += 3000
				else:
					currentTime = time.get_ticks()
					self.play_main_music(currentTime)
					self.screen.blit(self.background, (0, 0))
					self.allBlockers.update(self.screen)
					self.scoreText2 = Text(FONT, 20, str(self.score), GREEN, 85, 5)
					self.scoreText.draw(self.screen)
					self.scoreText2.draw(self.screen)
					self.livesText.draw(self.screen)
					# print state map before agent makes move
					self.get_action()

					# after agent makes move
					self.allSprites.update(self.keys, currentTime, self.killedRow, self.killedColumn, self.killedArray)

					# after sprites make move
					# TODO: investigate speed of bullets  and enemies move. might want to make it easier to predict next states by making all the sprites update only 1 frame before

					self.explosionsGroup.update(self.keys, currentTime)

					# before colision?
					#	print("printing before check_collisions")
					#	print("game state: ")
					#  self.get_state(Config.factor)
					#	print("reduced state")
					#	self.get_ships_immediate_proximity()
					self.check_collisions()
					self.create_new_ship(self.makeNewShip, currentTime)
					self.update_enemy_speed()

					if len(self.enemies) > 0:
						self.make_enemies_shoot()

			elif self.gameOver:
				currentTime = time.get_ticks()
				# Reset enemy starting position
				self.enemyPositionStart = self.enemyPositionDefault
				self.create_game_over(currentTime)
				scoreList.add((i, self.score))

				if (i >= it):
					break

			display.update()
			self.clock.tick(60)
		print(scoreList)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--iterations', type=int, required=True)
	args = parser.parse_args()
	game = SpaceInvaders()
	game.main(args.iterations)
