import random
import copy
from math import inf
from time import time

class GameError(AttributeError):
	pass

class Game:

	def __init__(self, n):
		self.size = n
		self.half_the_size = int(n/2)
		self.reset()

	def reset(self):
		self.board = []
		value = 'B'
		for i in range(self.size):
			row = []
			for j in range(self.size):
				row.append(value)
				value = self.opponent(value)
			self.board.append(row)
			if self.size%2 == 0:
				value = self.opponent(value)

	def __str__(self):
		result = "  "
		for i in range(self.size):
			result += str(i) + " "
		result += "\n"
		for i in range(self.size):
			result += str(i) + " "
			for j in range(self.size):
				result += str(self.board[i][j]) + " "
			result += "\n"
		return result

	def valid(self, row, col):
		return row >= 0 and col >= 0 and row < self.size and col < self.size

	def contains(self, board, row, col, symbol):
		return self.valid(row,col) and board[row][col]==symbol

	def countSymbol(self, board, symbol):
		count = 0
		for r in range(self.size):
			for c in range(self.size):
				if board[r][c] == symbol:
					count += 1
		return count

	def opponent(self, player):
		if player == 'B':
			return 'W'
		else:
			return 'B'

	def distance(self, r1, c1, r2, c2):
		return abs(r1-r2 + c1-c2)

	def makeMove(self, player, move):
		self.board = self.nextBoard(self.board, player, move)

	def nextBoard(self, board, player, move):
		r1 = move[0]
		c1 = move[1]
		r2 = move[2]
		c2 = move[3]
		next = copy.deepcopy(board)
		if not (self.valid(r1, c1) and self.valid(r2, c2)):
			raise GameError
		if next[r1][c1] != player:
			raise GameError
		dist = self.distance(r1, c1, r2, c2)
		if dist == 0:
			if self.openingMove(board):
				next[r1][c1] = "."
				return next
			raise GameError
		if next[r2][c2] != ".":
			raise GameError
		jumps = int(dist/2)
		dr = int((r2 - r1)/dist)
		dc = int((c2 - c1)/dist)
		for i in range(jumps):
			if next[r1+dr][c1+dc] != self.opponent(player):
				raise GameError
			next[r1][c1] = "."
			next[r1+dr][c1+dc] = "."
			r1 += 2*dr
			c1 += 2*dc
			next[r1][c1] = player
		return next

	def openingMove(self, board):
		return self.countSymbol(board, ".") <= 1

	def generateFirstMoves(self, board):
		moves = []
		moves.append([0]*4)
		moves.append([self.size-1]*4)
		moves.append([self.half_the_size]*4)
		moves.append([(self.half_the_size)-1]*4)
		return moves

	def generateSecondMoves(self, board):
		moves = []
		if board[0][0] == ".":
			moves.append([0,1]*2)
			moves.append([1,0]*2)
			return moves
		elif board[self.size-1][self.size-1] == ".":
			moves.append([self.size-1,self.size-2]*2)
			moves.append([self.size-2,self.size-1]*2)
			return moves
		elif board[self.half_the_size-1][self.half_the_size-1] == ".":
			pos = self.half_the_size -1
		else:
			pos = self.half_the_size
		moves.append([pos,pos-1]*2)
		moves.append([pos+1,pos]*2)
		moves.append([pos,pos+1]*2)
		moves.append([pos-1,pos]*2)
		return moves

	def check(self, board, r, c, rd, cd, factor, opponent):
		if self.contains(board,r+factor*rd,c+factor*cd,opponent) and \
		   self.contains(board,r+(factor+1)*rd,c+(factor+1)*cd,'.'):
			return [[r,c,r+(factor+1)*rd,c+(factor+1)*cd]] + \
				   self.check(board,r,c,rd,cd,factor+2,opponent)
		else:
			return []

	def generateMoves(self, board, player):
		if self.openingMove(board):
			if player=='B':
				return self.generateFirstMoves(board)
			else:
				return self.generateSecondMoves(board)
		else:
			moves = []
			rd = [-1,0,1,0]
			cd = [0,1,0,-1]
			for r in range(self.size):
				for c in range(self.size):
					if board[r][c] == player:
						for i in range(len(rd)):
							moves += self.check(board,r,c,rd[i],cd[i],1,
												self.opponent(player))
			return moves

	def playOneGame(self, p1, p2, show):
		self.reset()
		while True:
			if show:
				print(self)
				print("player B's turn")
			move = p1.getMove(self.board)
			if move == []:
				print("Game over")
				return 'W'
			try:
				self.makeMove('B', move)
			except GameError:
				print("Game over: Invalid move by", p1.name)
				print(move)
				print(self)
				return 'W'
			if show:
				print(move)
				print(self)
				print("player W's turn")
			move = p2.getMove(self.board)
			if move == []:
				print("Game over")
				return 'B'
			try:
				self.makeMove('W', move)
			except GameError:
				print("Game over: Invalid move by", p2.name)
				print(move)
				print(self)
				return 'B'
			if show:
				print(move)

	def playNGames(self, n, p1, p2, show):
		first = p1
		second = p2
		for i in range(n):
			print("Game", i)
			winner = self.playOneGame(first, second, show)
			if winner == 'B':
				first.won()
				second.lost()
				print(first.name, "wins")
			else:
				first.lost()
				second.won()
				print(second.name, "wins")
			# first, second = second, first


class Player:
	name = "Player"
	wins = 0
	losses = 0
	def results(self):
		result = self.name
		result += " Wins:" + str(self.wins)
		result += " Losses:" + str(self.losses)
		return result
	def lost(self):
		self.losses += 1
	def won(self):
		self.wins += 1
	def reset(self):
		self.wins = 0
		self.losses = 0

	def initialize(self, side):
		abstract()

	def getMove(self, board):
		abstract()


class SimplePlayer(Game, Player):
	def initialize(self, side):
		self.side = side
		self.name = "Simple"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		n = len(moves)
		if n == 0:
			return []
		else:
			return moves[0]

class RandomPlayer(Game, Player):
	def initialize(self, side):
		self.side = side
		self.name = "Random"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		n = len(moves)
		if n == 0:
			return []
		else:
			return moves[random.randrange(0, n)]

class HumanPlayer(Game, Player):
	def initialize(self, side):
		self.side = side
		self.name = "Human"
	def getMove(self, board):
		moves = self.generateMoves(board, self.side)
		while True:
			print("Possible moves:", moves)
			n = len(moves)
			if n == 0:
				print("You must concede")
				return []
			index = input("Enter index of chosen move (0-"+ str(n-1) +
						  ") or -1 to concede: ")
			try:
				index = int(index)
				if index == -1:
					return []
				if 0 <= index <= (n-1):
					print("returning", moves[index])
					return moves[index]
				else:
					print("Invalid choice, try again.")
			except Exception as e:
				print("Invalid choice, try again.")
			

class MinimaxPlayer(Game, Player):
	def initialize(self, side, depth):
		self.name = "Minimax"
		self.side = side
		self.depth = depth
		# self.moves = 0
		# self.move_time = 0
		# self.average_move_time = 0
	
	def getMove(self, board):
		# start = time()
		best_move_score = float(-inf)
		initial_alpha = float(-inf)
		initial_beta = float(inf)
		moves = self.generateMoves(board, self.side)
		if not moves:
			return []
		for move in moves:
			next_board = self.nextBoard(board, self.side, move)
			next_board_score = self.minValue(next_board, initial_alpha, initial_beta, 1)
			if next_board_score > best_move_score:
				best_move = move
				best_move_score = next_board_score
			if best_move_score > initial_beta:
				return best_move_score
			initial_alpha = max(initial_alpha, best_move_score)
		# move_time = time()-start
		# self.moves += 1
		# self.move_time += move_time
		# self.average_move_time = self.move_time/ self.moves
		# print("********")
		# print(self.moves)
		# print(self.move_time)
		# print("*******")
		return best_move
		
	def maxValue(self, board, alpha, beta, depth):
		if depth == self.depth:
			return self.evaluate(board)
		maximum = float(-inf)
		moves = self.generateMoves(board, self.side)
		if not moves:
			return self.evaluate(board)
		for move in moves:
			next_board = self.nextBoard(board, self.side, move)
			maximum = max(maximum, self.minValue(next_board, alpha, beta, depth+1))
			if maximum > beta:
				return maximum
			alpha = max(alpha, maximum)
		return maximum


	def minValue(self, board, alpha, beta, depth):
		if depth == self.depth:
			return self.evaluate(board)
		minimum = float(inf)
		moves = self.generateMoves(board, self.opponent(self.side))
		if not moves:
			return self.evaluate(board)
		for move in moves:
			next_board = self.nextBoard(board, self.opponent(self.side), move)
			minimum = min(minimum, self.maxValue(next_board, alpha, beta, depth+1))
			if minimum < alpha:
				return minimum
			beta = min(beta, minimum)
		return minimum

	def evaluate(self, board):
		my_moves = self.generateMoves(board, self.side)
		my_movable_pieces = {(move[0], move[1]) for move in my_moves}
		if not my_moves:
			return -1000 # Loosing point
		opponent_moves = self.generateMoves(board, self.opponent(self.side))
		opp_movable_pieces = {(move[0], move[1]) for move in opponent_moves}
		if not opponent_moves:
			return 1000 # Winning point
		first_eval = len(my_moves) / len(opponent_moves)
		second_eval = len(my_movable_pieces)/len(opp_movable_pieces)
		return first_eval + 2 * second_eval
	
if __name__ == '__main__':
	game = Game(8)
	player1 = MinimaxPlayer(8)
	player1.initialize('B', 5)
	player2 = RandomPlayer(8)
	player2.initialize('W')
	game.playOneGame(player1, player2, False)
	# print(player1.average_move_time)
	# game.playNGames(50, player1, player2, False)
	# print(player1.results())