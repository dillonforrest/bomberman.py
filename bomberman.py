"""
Bomberman emulation made in Hacker School.
Not intended to infringe on any copyrights.
Made in the interest of improving my programming and as an ode to Bomberman.
-Dillon 23 July 2012
"""
#!/usr/bin/python

import pygame, sys, os
from pygame.locals import *
from pprint import pprint

# Game constants and global variables
debug = True
b = 40 # pixel width for one block
NB_ACR = 8 # number blocks across -- should be an even number
NB_DOWN = 6 # number blocks down -- should be an even number
game_width = b * (NB_ACR * 2 + 1)
game_height = b * (NB_DOWN * 2 + 1)

#  Colors
BLACK = (0,0,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
DARK_GREY = (140,140,140)
ORANGE = (255,108,10)
BG_COLOR = BLACK

class IterRegistry(type):
	def __iter__(cls):
		return iter(cls._registry)


window = pygame.display.set_mode( (game_width,game_height) )
class Game():
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Bomberman by Dillon Forrest")
		self.bbman = Bomberman()
		self.arena = Arena(self.bbman)

	def mainLoop(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT: sys.exit()
			self.bbman.processKeyboardEvents(self.arena)
			self.processBombs()
			self.updateGameStats(Bomb, Explosion)
			self.draw()
	
	def processBombs(self):
		for explosion in Explosion:
			if explosion.life > 0: explosion.life -= 1
		for bomb in Bomb:
			if bomb.life > 0:
				bomb.life -= 1
				if bomb.life == 0: Explosion(bomb, self.arena)

	def updateGameStats(self, Bomb, Explosion):
		Bomb = [bomb for bomb in Bomb if bomb.life > 0]
		for player in Bomberman:
			player.bombs = len( [bomb for bomb in Bomb if bomb.owner==player] )
			if player.bomb_reset > 0: player.bomb_reset -= 1
		Explosion = [expl for expl in Explosion if expl.life > 0]

	def draw(self):
		window.fill(BG_COLOR)
		window.lock()
		self.arena.drawArena()
		self.bbman.drawBomberman()
		for bomb in Bomb:
			if bomb.life > 0:	bomb.drawBomb()
		for explosion in Explosion:
			if explosion.life > 0: explosion.drawExplosion()
		window.unlock()
		pygame.display.flip()

class Bomberman():
	__metaclass__ = IterRegistry
	_registry = []

	def __init__(self):
		self._registry.append(self)
		self.radius = 10
		self.x, self.y = self.radius, self.radius # initial position
		self.w = 2*self.radius
		self.speed = 3 # I think this is pixels per frame
		self.bombs = 0
		self.bomb_max = 3
		self.bomb_reset = 0
		self.reset_amt = 10 # frames

	def isUpDownOkay(self, x, y, arena):
		w, r = self.w, self.radius
		hz, vt = arena.hz_aisles, arena.vt_aisles
		if y < 0+r or y >= game_height-w+r: return False
		# make sure x position is okay
		for aisle in hz:
			if aisle[0] <= x <= aisle[1] - w: return True
			else:
				for aisle in vt:
					if aisle[0] <= y <= aisle[1] - w: return True
		else: return False
		
	def isLeftRightOkay(self, x, y, arena):
		w = self.w; r = self.radius
		hz = arena.hz_aisles; vt = arena.vt_aisles
		if x < 0+r or x >= game_width-w+r: return False
		# make sure y position is okay
		for aisle in vt:
			if aisle[0] <= y <= aisle[1] - w: return True
			else:
				for aisle in hz:
					if aisle[0] <= x <= aisle[1] - w: return True
		else:	return False

	def isMovementOkay(self, move, arena):
		w, r = self.w, self.radius
		hz, vt = arena.hz_aisles, arena.vt_aisles
		for new,game,aisles,rev_aisles,rev_new in ( 
			(move[0], game_width, hz, vt, move[1]),	
			(move[1], game_height, vt, hz, move[0]) ):
			if  new < r or new > game-r: return False
			for aisle in aisles:
				if aisle[0] <= new <= aisle[1]-w: return True
				else:
					for aisle in rev_aisles:
						if aisle[0] <= rev_new <= aisle[1]-w: return True
			else: return False
	
	def processKeyboardEvents(self, arena):
		keys = pygame.key.get_pressed()
		x, y, s = self.x, self.y, self.speed
		if keys[pygame.K_UP]:
			if self.isMovementOkay( (x,y-s), arena): self.y -= s
		elif keys[pygame.K_DOWN]:
			if self.isMovementOkay( (x,y+s), arena): self.y += s
		elif keys[pygame.K_LEFT]:
			if self.isMovementOkay( (x-s,y), arena): self.x -= s
		elif keys[pygame.K_RIGHT]:
			if self.isMovementOkay( (x+s,y), arena): self.x += s
		elif keys[pygame.K_SPACE]: self.dropBomb(arena)


	def dropBomb(self, arena):
		if self.bomb_reset == 0:
			if self.bombs < self.bomb_max:
				Bomb(self, arena)
				self.bomb_reset = self.reset_amt

	def drawBomberman(self):
		pygame.draw.circle(window, WHITE, (self.x, self.y),	self.radius)

class Bomb():
	__metaclass__ = IterRegistry
	_registry = []

	def __init__(self, bbman, arena):
		self._registry.append(self)
		self.life = 150 # frames
		self.radius = 20 # pixels
		self.color = DARK_GREY
		self.x, self.y = self.findBombPos(bbman, arena)
		self.owner = bbman

	def findBombPos(self, bbman, arena):
		bbx = bbman.x + bbman.radius; bby = bbman.y + bbman.radius
		pos = [0,0]
		hz_tiles = arena.bombx; vt_tiles = arena.bomby
		for tiles, bb, n in ( (hz_tiles,bbx,0), (vt_tiles,bby,1) ):
			for tile in tiles:
				if tile[0] < bb <= tile[1]: pos[n] = sum(tile)/len(tile)
		return pos[0], pos[1]

	def drawBomb(self):
		pygame.draw.circle(window, self.color, (self.x,self.y), self.radius)

class Explosion():
	__metaclass__ = IterRegistry
	_registry = []

	def __init__(self, bomb, arena):
		self._registry.append(self)
		self.x, self.y = bomb.x, bomb.y
		self.radius = 8 # tiles, not pixels
		self.area = self.findExplArea(arena)
		self.life = 30 # frames
		self.arena = arena
		# the self.arena attribute is necessary to recursively
		# instantiate more explosions within the Explosion class

	def findExplArea(self, arena):
		typee = self.find2or4WayExpl(arena)
		r = self.radius
		full, half, short = (r*2 + 1)*b, (r+0.5)*b, (0.5*b)
		if typee == '2-way hz':
			hz_blast, vt_blast = ( self.x-half,self.y-short,full,b ), (0,0,0,0)
		elif typee == '2-way vt':
			hz_blast, vt_blast = (0,0,0,0), ( self.x-short,self.y-half,b,full )
		else: # typee == '4-way':
			hz_blast = ( self.x-half,self.y-short,full,b )
			vt_blast = ( self.x-short,self.y-half,b,full )
		return hz_blast, vt_blast
	
	def find2or4WayExpl(self, arena):
		x, y, path = self.x, self.y, [0,0]
		for aisles,center,p in ( (arena.bombx,x,1),(arena.bomby,y,0) ):
			for n in aisles:
				if n[0] < center < n[1]:
					if aisles.index(n) % 2 == 0: path[p] = 'open'
					else: path[p] = 'closed'
		if path[0] == 'open' and path[1] == 'open': return '4-way'
		elif path[0] == 'open' and path[1] == 'closed': return '2-way hz'
		elif path[0] == 'closed' and path[1] == 'open': return '2-way vt'

	def isInExplArea(self, bomb):
		for blast in self.area:
			if blast[0] < bomb.x <= blast[0]+blast[2] \
				and blast[1] < bomb.y <= blast[1]+blast[3]:
				return True

	def findNearbyBombs(self):
		return [bomb for bomb in Bomb if self.isInExplArea(bomb)]

	def drawExplosion(self):
		for i in range(2): pygame.draw.rect(window, ORANGE, self.area[i])
		more_exploding_bombs = self.findNearbyBombs()
		for bomb in more_exploding_bombs:
			if bomb.life > 0:
				bomb.life = 0
				Explosion(bomb, self.arena)

class Arena():
	def __init__(self, bbman):
		self.array = [ [ ( b*(2*x+1),b*(2*y+1) ) for y in range(NB_DOWN) ] \
			for x in range(NB_ACR) ]
		r = bbman.radius
		self.hz_aisles = [ ( 2*x*b+r,(2*x+1)*b+r ) for x in range(NB_ACR+1) ]
		self.vt_aisles = [ ( 2*y*b+r,(2*y+1)*b+r ) for y in range(NB_ACR+1) ]
		# self.bombi = ( start of tile, end of tile, index of tile )
		self.bombx = [ ( b*x, b*(x+1) ) for x in range(2*NB_ACR + 1) ]
		self.bomby = [ ( b*y, b*(y+1) ) for y in range(2*NB_DOWN + 1) ]
	def drawArena(self):
		for x in range(NB_ACR):
			for y in range(NB_DOWN):
				pygame.draw.rect(window, BLUE, pygame.Rect(self.array[x][y],(b,b)))

if __name__ == '__main__':
	game = Game()
	game.mainLoop()
