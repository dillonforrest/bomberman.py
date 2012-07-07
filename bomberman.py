#!/usr/bin/python
"""

Insert comments here.

"""


import pygame, sys, os
from pygame.locals import *

debug = True
BLOCK_WIDTH = 40 # pixels
N_BLOCKS_ACR = 8 # should be even number
N_BLOCKS_DOWN = 6 # should be even number
AISLE_BUFFER = 10 # = total aisle width - block width (in pixels)
aisle_width = BLOCK_WIDTH + AISLE_BUFFER
game_width = N_BLOCKS_ACR*BLOCK_WIDTH + (N_BLOCKS_ACR+1)*(aisle_width)
game_height = N_BLOCKS_DOWN*BLOCK_WIDTH + (N_BLOCKS_DOWN+1)*(aisle_width)
RADIUS = 10
# ROOT = os.path.dirname(os.path.abspath(sys.argv[0]))
# Arena
block_array = []
for x in range(N_BLOCKS_ACR):
	block_array.append([])
	for y in range(N_BLOCKS_DOWN):
		x_pos = x*BLOCK_WIDTH + (x+1)*(aisle_width)
		y_pos = y*BLOCK_WIDTH + (y+1)*(aisle_width)
		block_array[x].append((x_pos,y_pos))
# Bomb array
bomb_row = [ (-RADIUS, aisle_width), (-RADIUS+aisle_width, BLOCK_WIDTH) ]
bomb_col = [ (-RADIUS, aisle_width), (-RADIUS+aisle_width, BLOCK_WIDTH) ]
bomb_array = []
for x in range(N_BLOCKS_ACR*2-1):
	bomb_row.append( (bomb_row[-1][0]+bomb_row[-1][1], bomb_row[-2][1]) )
for y in range(N_BLOCKS_DOWN*2-1):
	bomb_col.append( (bomb_col[-1][0]+bomb_col[-1][1], bomb_col[-2][1]) )	
for x in bomb_row:
	bomb_array.append([])
	for y in bomb_col:
		bomb_array[-1].append( ( x[0],y[0],x[1],y[1] ) )
# Colors
BLACK = (0,0,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
DARK_GREY = (140,140,140)
ORANGE = (255,108,10)
BG_COLOR = BLACK
# Bomberman stats
pos = (0,0) # starting position
MOVEMENT = 3 # walking speed
# Bomb specs
BOMB_LIFE = 150
EXPLOSION_LIFE = 30
EXPLOSION_RADIUS = 8 # tiles, not pixels
MAX_BOMBS = 3
BOMB_RESET = 10
bomb_reset_timer = 0
bomb_inventory = []
for blah in range(MAX_BOMBS):
	bomb_inventory.append([0,0,0,0]) #bomb_timer,explosion_timer,bomb.x,bomb.y

def isYMovementOkay(x,y):
	if y < 0: return False
	if y >= 0 and y <= aisle_width - 2*RADIUS: return True
	if y >= game_height - 2*RADIUS: return False
    # make sure x_pos is proper
	if x <= aisle_width - 2*RADIUS: return True
	for row in block_array:
		if x>=BLOCK_WIDTH+row[0][0] and x<=BLOCK_WIDTH+row[0][0]+aisle_width-2*RADIUS:
			return True
		else:
			for column in block_array[0]:
				if y>=BLOCK_WIDTH+column[1] and (y<=BLOCK_WIDTH+column[1]+
					aisle_width-2*RADIUS):
					return True			
	else: return False

def isXMovementOkay(x,y):
	if x <= 0: return False
	if x >= 0 and x <= aisle_width - 2*RADIUS: return True
	if x >= game_width - 2*RADIUS: return False
	# make sure y_pos is proper
	if y <= aisle_width - 2*RADIUS: return True
	for column in block_array[0]:
		if y>=BLOCK_WIDTH+column[1] and y<=BLOCK_WIDTH+column[1]+aisle_width-2*RADIUS:
			return True
		else:
			for row in block_array:
				if x>=BLOCK_WIDTH+row[0][0] and (x<=BLOCK_WIDTH+row[0][0]+
					aisle_width-2*RADIUS):
					return True
	else: return False

window = pygame.display.set_mode((game_width,game_height))

class Game():
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Bomberman by Dillon Forrest")
		self.arena = Arena()
		self.bomberman = Bomberman()
		
	def keyboardEvents(self, bomberman):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			bomberman.moveUp()
		elif keys[pygame.K_DOWN]:
			bomberman.moveDown()
		elif keys[pygame.K_LEFT]:
			bomberman.moveLeft()
		elif keys[pygame.K_RIGHT]:
			bomberman.moveRight()
		elif keys[pygame.K_SPACE]:
			self.bomb = Bomb()
			return "bomb"

	def mainLoop(self):
		global bomb_reset_timer
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					sys.exit()
			self.draw(self.arena, self.bomberman)
			self.keyboardEvents(self.bomberman)
			if bomb_reset_timer > 0: bomb_reset_timer -= 1
			if self.keyboardEvents(self.bomberman) == "bomb":
				if self.bomb.isEmptyTile(self.bomberman.x,self.bomberman.y,bomb_inventory):
					if bomb_reset_timer <= 0:
						bomb_reset_timer = BOMB_RESET
						for i, bomb_spec in enumerate(bomb_inventory):
							if bomb_spec[0] == 0 and bomb_spec[1] == 0:
								bomb_inventory[i][0] = BOMB_LIFE
								bomb_inventory[i][2] = self.bomberman.x
								bomb_inventory[i][3] = self.bomberman.y
								break
			for i, bomb_spec in enumerate(bomb_inventory):
				if bomb_spec[0] > 0:
					self.bomb.drawBomb(bomb_spec[2],bomb_spec[3])
					bomb_inventory[i][0] -= 1
					if bomb_inventory[i][0] <= 0:
						bomb_inventory[i][1] = EXPLOSION_LIFE
				if bomb_spec[1] > 0:
					self.bomb.drawExplosion(bomb_spec[2],bomb_spec[3])
					bomb_inventory[i][1] -= 1
			pygame.display.flip()
	
	def draw(self, arena, bomberman):
		window.fill(BG_COLOR)
		arena.drawBlocks()
		bomberman.drawBomberman()
		
class Bomberman():
	def __init__(self):
		self.x = pos[0]
		self.y = pos[1]

	def moveUp(self):
		if isYMovementOkay(self.x,self.y-MOVEMENT):
			self.y -= MOVEMENT
	def moveDown(self):
		if isYMovementOkay(self.x,self.y+MOVEMENT):
			self.y += MOVEMENT
	def moveLeft(self):
		if isXMovementOkay(self.x-MOVEMENT,self.y):
			self.x -= MOVEMENT
	def moveRight(self):
		if isXMovementOkay(self.x+MOVEMENT,self.y):
			self.x += MOVEMENT
		
	def drawBomberman(self):
		window.lock()
		pygame.draw.circle(window, WHITE, (self.x+RADIUS,self.y+RADIUS), RADIUS)
		window.unlock()
		
class Bomb():
	def __init__(self):
		pass
		
	def findBombPos(self, x_pos, y_pos):
		for row in bomb_array:
			if x_pos > row[0][0] and x_pos <= row[0][0]+row[0][2]:
				for col in row:
					if y_pos > col[1] and y_pos <= col[1]+col[3]:
						return col[0]+col[2]/2+RADIUS,col[1]+col[3]/2+RADIUS,col[2],col[3]

	def drawBomb(self,x,y):
		center_x, center_y, tile_width, tile_height = self.findBombPos(x,y)
		window.lock()
		pygame.draw.circle(window, DARK_GREY, (center_x, center_y), BLOCK_WIDTH/2)
		window.unlock()
		
	def isEmptyTile(self,bbman_x,bbman_y,bomb_list):
		results = self.findBombPos(bbman_x,bbman_y)
		x,y = results[0],results[1]
		for bomb in bomb_list:
			if bomb[0] != 0:
				container = self.findBombPos(bomb[2],bomb[3])
				if container[0] == x and container[1] == y:
					return False
		else: return True
		
	def explosionArea(self,x,y):
		center_x, center_y, tile_width, tile_height = self.findBombPos(x,y)
		if tile_width == aisle_width and tile_height == aisle_width:
			hz_top = center_y - aisle_width/2
			hz_height = aisle_width
			vt_left = center_x - aisle_width/2
			vt_width = aisle_width
			hz_left = center_x-aisle_width/2 - EXPLOSION_RADIUS/2*(aisle_width+
				BLOCK_WIDTH) - BLOCK_WIDTH*(EXPLOSION_RADIUS%2)
			vt_top = center_y-aisle_width/2 - EXPLOSION_RADIUS/2*(aisle_width+
				BLOCK_WIDTH) - BLOCK_WIDTH*(EXPLOSION_RADIUS%2)
			hz_width = (center_x - hz_left) * 2
			vt_height = (center_y - vt_top) * 2
		if tile_width == aisle_width and tile_height == BLOCK_WIDTH:
			hz_left = hz_top = hz_width = hz_height = 0
			vt_left = center_x - aisle_width/2
			vt_width = aisle_width
			vt_top = center_y-BLOCK_WIDTH/2 - EXPLOSION_RADIUS/2*(aisle_width+
				BLOCK_WIDTH) - aisle_width*(EXPLOSION_RADIUS%2)
			vt_height = (center_y - vt_top) * 2
		if tile_width == BLOCK_WIDTH and tile_height == aisle_width:
			vt_left = vt_top = vt_width = vt_height = 0
			hz_top = center_y - aisle_width/2
			hz_height = aisle_width
			hz_left = center_x - BLOCK_WIDTH/2 - EXPLOSION_RADIUS/2*(aisle_width+
				BLOCK_WIDTH) - aisle_width*(EXPLOSION_RADIUS%2)
			hz_width = (center_x - hz_left) * 2
		return hz_left,hz_top,hz_width,hz_height,vt_left,vt_top,vt_width,vt_height
	
	def isInArea(self,area,x,y):
		hz_leftbound = area[0]; hz_rightbound = area[0]+area[2]
		hz_upperbound = area[1]; hz_lowerbound = area[1]+area[3]
		vt_leftbound = area[4]; vt_rightbound = area[4]+area[6]
		vt_upperbound = area[5]; vt_lowerbound = area[5]+area[7]
		if x >= hz_leftbound and x <= hz_rightbound:
			if y >= hz_upperbound and y <= hz_lowerbound:
				return True
		if x >= vt_leftbound and x <= vt_rightbound:
			if y >= vt_upperbound and y <= vt_lowerbound:
				return True
		else: 
			return False
		
	def findNearbyBombs(self, bomb_x, bomb_y):
		area = self.explosionArea(bomb_x,bomb_y)
		exploding_list = []
		for bomb in bomb_inventory:
			if bomb[0] > 0:
				if self.isInArea(area,bomb[2],bomb[3]):
					exploding_list.append(bomb)
		return exploding_list
	
	def drawExplosion(self,x,y):
		area = self.explosionArea(x,y)
		window.lock()
		pygame.draw.rect(window, ORANGE, (area[0],area[1],area[2],area[3]))
		pygame.draw.rect(window, ORANGE, (area[4],area[5],area[6],area[7]))
		window.unlock()
		position = self.findBombPos(x,y)
		more_explosions = self.findNearbyBombs(position[0],position[1])
		# change bomb_inventory to address side bombs exploding
		for explosion in more_explosions:
			for i, bomb in enumerate(bomb_inventory):
				if explosion[2] == bomb[2] and explosion[3] == bomb[3]:
					bomb_inventory[i][0] = 0
					bomb_inventory[i][1] = EXPLOSION_LIFE
		for i, explosion in enumerate(more_explosions):
			if explosion[0] > 0:
				self.drawExplosion(explosion[2],explosion[3])

class Arena():
	def __init__(self):
		pass
	def drawBlocks(self):
		window.lock()
		for x in range(N_BLOCKS_ACR):
			for y in range(N_BLOCKS_DOWN):
				pygame.draw.rect(window, BLUE,
					pygame.Rect(block_array[x][y], (BLOCK_WIDTH,BLOCK_WIDTH) ))
		window.unlock()
					
if __name__ == '__main__':
	game = Game()
	game.mainLoop()