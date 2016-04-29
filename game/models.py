from __future__ import unicode_literals

from django.db import models

class Channel(models.Model):
	channel_id = models.CharField(max_length=32)

class Player(models.Model):
        username = models.CharField(max_length=32)
        channel = models.ForeignKey(Channel, default=None, null=True)

class Board(models.Model):
	# Config is the base 10 equivalent of the board represented as a base 3 number.
	# Where empty spaces are 0, X is 1 and O is 2.
	# For example: X | O | X     1 | 2 | 1
	#  	       ---------     ---------
	#              O | X | O  => 2 | 1 | 2 => 121212120 in base 3 => 12300 in base 10 = config
	#              ---------     ---------
	# 	       X | O |       1 | 2 | 0
	config = models.IntegerField(default=0) 
	game_over = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	channel = models.ForeignKey(Channel, default=None, null=True)
	playerX = models.ForeignKey(Player, default=None, related_name='playerX')
	playerO = models.ForeignKey(Player, default=None, related_name='playerO')
	
	def __str__(self):
		return '\n\n {0} | {1} | {2}\n----------\n {3} | {4} | {5}\n----------\n {6} | {7} | {8}'.format(*self.convertBoardToListOfPlayers()).replace('0', '  ').replace('1', 'X').replace('2', 'O')

	def getLetterAtPosition(self, position):
		if (position < 0 or position > 8):
			return -1
		else:
			return self.config / (3 ** (8 - position)) % 3;
	
	def setLetterAtPosition(self, letter, position):
		if (position < 0 or position > 8):
			return -1
		else:
			self.config += letter * (3 ** (8 - position))
			return self.config
			
	def convertBoardToListOfPlayers(self):
		return [self.getLetterAtPosition(i) for i in range(9)]

	def determineWinner(self):
		# Check all winning combinations.
		winningCombinations = [[0, 1, 2], # top row
			[3, 4, 5], # middle row
			[6, 7, 8], # bottom row
			[0, 3, 6], # left column
			[1, 4, 7], # middle column
			[2, 5, 8], # right column
			[0, 4, 8], # top left to bottom right diagonal
			[2, 4, 6]] # top right to bottom left diagonal
		listOfPlayers = self.convertBoardToListOfPlayers()
		for winningCombination in winningCombinations:
			listOfPlayersAtWinningIndices = [listOfPlayers[position] for position in winningCombination]
			# If all of the spaces in winning combinations are the same player.
			if (listOfPlayersAtWinningIndices.count(listOfPlayersAtWinningIndices[0]) == len(listOfPlayersAtWinningIndices)):
				# And they are not all empty.
				if (listOfPlayersAtWinningIndices[0] != 0):
					# Return winner.
					return listOfPlayersAtWinningIndices[0]
		return 0

	def isDraw(self):
		# There is no winner and no empty spaces left on the board.
		return self.determineWinner() == 0 and self.convertBoardToListOfPlayers().count(0) == 0

	def determineWhichPlayerHasNextMove(self):
		listOfPlayers = self.convertBoardToListOfPlayers() 
		if (listOfPlayers.count(1) == listOfPlayers.count(2)):
			return 1 # Player X goes first and when there are equal number of Xs and Os on the board.
		else:
			return 2

