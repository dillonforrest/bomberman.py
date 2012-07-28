"""
Bomberman emulation made in Hacker School.
Not intended to infringe on any copyrights.
Made in the interest of improving my programming and as an ode to Bomberman.
-Dillon 23 July 2012
"""
#!/usr/bin/python

import pygame, sys, os, random
from pygame.locals import *
from pprint import pprint

# Game constants
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
PINK = (255,51,102)
GREEN = (51,255,102)
YELLOW = (204,255,51)

class IterRegistry(type):
	def __iter__(cls):
		return iter(cls._registry)


window = pygame.display.set_mode( (game_width,game_height) )
class Game():
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Bomberman by Dillon Forrest")
		self.arena = Arena()
		self.players = [
			Bomberman(self.arena, WHITE, self.arena.start0),
			AIBot(self.arena, PINK, self.arena.start1),
			AIBot(self.arena, GREEN, self.arena.start2),
			AIBot(self.arena, YELLOW, self.arena.start3),
		]

	def mainLoop(self):
		while True:
			for event in pygame.event.get():
				if event.type == QUIT: sys.exit()
			self.players[0].processKeyboardEvents(self.arena)
			self.updateBots(AIBot)
			self.processBombs()
			self.killBombermen(Explosion)
			self.updateGameStats(Bomb, Explosion)
			self.draw()

	def updateBots(self, AIBot):
		for bot in AIBot:
			bot.update()
	
	def processBombs(self):
		for explosion in Explosion:
			if explosion.life > 0: explosion.life -= 1
		for bomb in Bomb:
			if bomb.life > 0:
				bomb.life -= 1
				if bomb.life == 0: Explosion(bomb, self.arena)

	def killBombermen(self, Explosion):
		for player in self.players:
			for expl in Explosion:
				if expl.isInExplArea(player.x, player.y):
					if player.alive == True:
						print "lul you killed him"					
						player.alive = False

	def updateGameStats(self, Bomb, Explosion):
		Bomb._registry = [bomb for bomb in Bomb if bomb.life > 0]
		for player in self.players:
			player.bombs = len( [bomb for bomb in Bomb if bomb.owner==player] )
			if player.bomb_reset > 0: player.bomb_reset -= 1
		Explosion._registry = [expl for expl in Explosion if expl.life > 0]
		# add game-over logic
		count = 0
		winner = None 
		for player in self.players:
			if player.alive:
				count += 1
				winner = player
		if count == 0:
			print("Draw!")
			sys.exit()
		elif count == 1:
			print("Player", player, "has won!")
			sys.exit()
			
	def draw(self):
		window.fill(BG_COLOR)
		window.lock()
		self.arena.drawArena()
		for bomberman in self.players:
			if bomberman.alive:
				bomberman.drawBomberman()
		for bomb in Bomb:
			if bomb.life > 0:	bomb.drawBomb()
		for explosion in Explosion:
			if explosion.life > 0: explosion.drawExplosion()
		window.unlock()
		pygame.display.flip()

class Bomberman():
	__metaclass__ = IterRegistry
	_registry = []

	def __init__(self, arena, color, start_pos):
		self._registry.append(self)
		self.radius = arena.bbmanradius
		self.x, self.y = start_pos # initial position
		self.w = 2*self.radius
		self.speed = 3 # I think this is pixels per frame
		self.bombs = 0
		self.bomb_max = 3
		self.bomb_reset = 0
		self.reset_amt = 10 # frames
		self.color = color
		self.alive = True
		self.arena = arena

	def isInBounds(self, move):
		r = self.radius
		for m, border in ( (move[0],game_width-r),(move[1],game_height-r) ):
			if m < r or m > border: return False
		return True

	def isInAisle(self, new, old, aisles):
		''' new = proposed new move; old = old move of opposite direction '''
		for aisle in aisles:
			if aisle[0] <= old <= aisle[1]: 
				return True
		return False

	def isHittingBlock(self, new, blocks):
		return not any([block[0] <= new <= block[1] for block in blocks])
		
	def isMoveOkay(self, newmove, oldmove, arena):
		r = self.radius
		if not self.isInBounds(newmove): return False
		if newmove[1] == oldmove[1]: data = { 
			'new':newmove[0], 'constant':newmove[1], 'aisles':arena.vt_aisles,
			'blocks':arena.hz_aisles }
		else: data = {
			'new':newmove[1], 'constant':newmove[0], 'aisles':arena.hz_aisles,
			'blocks':arena.vt_aisles }
		if not self.isInAisle(data['new'],data['constant'],data['aisles']): 
			if self.isHittingBlock(data['new'],data['blocks']): 
				return False
			else:
				return True
		else: return True
	
	def processKeyboardEvents(self, arena):
		keys = pygame.key.get_pressed()
		x, y, s = self.x, self.y, self.speed
		if keys[pygame.K_SPACE]: self.dropBomb(arena)
		elif keys[pygame.K_UP]    and self.isMoveOkay( (x,y-s), (x,y), arena ):
			self.y -= s
		elif keys[pygame.K_DOWN]  and self.isMoveOkay( (x,y+s), (x,y), arena ):
			self.y += s
		elif keys[pygame.K_LEFT]  and self.isMoveOkay( (x-s,y), (x,y), arena ):
			self.x -= s
		elif keys[pygame.K_RIGHT] and self.isMoveOkay( (x+s,y), (x,y), arena ):
			self.x += s

	def dropBomb(self, arena):
		if self.bomb_reset == 0:
			if self.bombs < self.bomb_max:
				Bomb(self, arena)
				self.bomb_reset = self.reset_amt

	def update(self):
		pass

	def drawBomberman(self):
		pygame.draw.circle(window, self.color, (self.x, self.y),	self.radius)

class AIBot(Bomberman):

	movedict = [(0,-1),(1,0),(0,1),(-1,0)]

	def __init__(self, arena, color, pos):
		Bomberman.__init__(self, arena, color, pos)
		self.direction = random.choice(self.movedict)
		
	def findGridPos(self):
		return self.x/b + 1, self.y/b + 1

	def move(self, destination):
		pos = self.findGridPos()
		graph = self.grid_to_adjdict()
		dead = []
		explore = {pos: 0}
		path = {pos: [pos]}
		while destination not in explore.keys():
			minn, minv = None, 10000 #10000 is an approximation of infinity
			
			for node in explore:
				cost = explore[node]
				if cost < minv:
					minn = node
					minv = cost
			for neighbor in graph[minn]:
				if not (neighbor in dead or neighbor in explore):
					explore[neighbor] = minv + 1
					path[neighbor] = path[minn] + [neighbor]
					break
			kill = True
			for neighbor in graph[minn]:
				if not (neighbor in dead  or neighbor in explore):
					kill = False
					break
			if kill:
				del explore[minn]
				dead.append(minn)
		return path[destination]

		#for x in self.arena.grid
		#	for y in x 

		destx, desty = destination
	
	def grid_to_adjdict(self):
		d = {}
		grid = self.arena.grid
		for i_, x in enumerate(grid[1:-1]):
			i = i_ + 1
			for j_, y in enumerate(x[1:-1]):
				j = j_ + 1
				d[(i, j)] = []
				if grid[i+1][j] == 0:
					d[(i, j)].append((i+1, j)) 
				if grid[i][j+1] == 0:
					d[(i, j)].append((i, j+1)) 
				if grid[i-1][j] == 0:
					d[(i, j)].append((i-1, j)) 
				if grid[i][j-1] == 0:
					d[(i, j)].append((i, j-1)) 
		return d


	def LALAgrid_to_adjdict(self):
		d = {}
		grid = self.arena.grid
		for i, x in enumerate(grid[1:-1]):
			for j, y in enumerate(x[1:-1]):
				d[(i, j)] = []
				if grid[i+1][j] == 0:
					d[(i, j)].append((i+1, j)) 
				if grid[i][j+1] == 0:
					d[(i, j)].append((i, j+1)) 
				if grid[i-1][j] == 0:
					d[(i, j)].append((i-1, j)) 
				if grid[i][j-1] == 0:
					d[(i, j)].append((i, j-1)) 
		return d

	def update(self):
		if random.randint(1, 100) == 100:
			self.direction = random.choice(self.movedict)
		if random.randint(1, 100) == 100:
			pass
			self.dropBomb(self.arena)
		movex = self.direction[0] * self.speed
		movey = self.direction[1] * self.speed
		for _ in range(10):
			if self.isMoveOkay((self.x+movex, self.y+movey),
			                   (self.x,self.y), self.arena):
				self.x += movex
				self.y += movey
				break
			else:
				self.direction = random.choice(self.movedict)
		for expl in Explosion:
			if expl.isInExplArea(self.x, self.y):
				self.direction = random.choice(self.movedict)

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
		if   path[0] == 'open'   and path[1] == 'open':   return '4-way'
		elif path[0] == 'open'   and path[1] == 'closed': return '2-way hz'
		elif path[0] == 'closed' and path[1] == 'open':   return '2-way vt'

	def isInExplArea(self, x, y):
		for blast in self.area:
			if blast[0] < x <= blast[0]+blast[2] \
				and blast[1] < y <= blast[1]+blast[3]:
				return True

	def findNearbyBombs(self):
		return [bomb for bomb in Bomb if self.isInExplArea(bomb.x,bomb.y)]

	def drawExplosion(self):
		for i in range(2): pygame.draw.rect(window, ORANGE, self.area[i])
		more_exploding_bombs = self.findNearbyBombs()
		for bomb in more_exploding_bombs:
			if bomb.life > 0:
				bomb.life = 0
				Explosion(bomb, self.arena)

class Arena():
	def __init__(self):
		self.array = [ [ ( b*(2*x+1),b*(2*y+1) ) for y in range(NB_DOWN) ] \
			for x in range(NB_ACR) ]
		self.hz_blocks = [ ( b*(2*x+1),b*(2*x+2) ) for x in range(NB_ACR) ]
		self.vt_blocks = [ ( b*(2*y+1),b*(2*y+2) ) for y in range(NB_DOWN) ]
		self.bbmanradius = 10 # pixel radius of bomberman and enemies
		r = self.bbmanradius
		self.hz_aisles = [ ( 2*x*b+r,(2*x+1)*b-r ) for x in range(NB_ACR+1) ]
		self.vt_aisles = [ ( 2*y*b+r,(2*y+1)*b-r ) for y in range(NB_ACR+1) ]
		# self.bombi = ( start of tile, end of tile, index of tile )
		self.bombx = [ ( b*x, b*(x+1) ) for x in range(2*NB_ACR + 1) ]
		self.bomby = [ ( b*y, b*(y+1) ) for y in range(2*NB_DOWN + 1) ]
		self.start0 = ( r, r)
		self.start1 = ( r, game_height-r)
		self.start2 = ( game_width-r, r)
		self.start3 = ( game_width-r, game_height-r)
		self.grid = [ [ 0 for y in range(game_height/b) ] \
			for x in range(game_width/b) ]
		for i, x in enumerate(self.grid):
			for j, y in enumerate(x):
				if i % 2 == 1 and j % 2 == 1:
					self.grid[i][j] = 1
		newgrid = [ [1 for y in range(game_height/b + 2)] ]
		for x in self.grid:
			newgrid.append( [1] + x + [1] )
		newgrid.append( [1 for y in range(game_height/b + 2)] )
		self.grid = newgrid

	def drawArena(self):
		for x in range(NB_ACR):
			for y in range(NB_DOWN):
				pygame.draw.rect(window, BLUE, pygame.Rect(self.array[x][y],(b,b)))

if __name__ == '__main__':
	game = Game()
	game.mainLoop()
