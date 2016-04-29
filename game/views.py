from django.shortcuts import render
from models import Player, Board, Channel
from django.http import JsonResponse
import logging

def index(request):
	token = request.GET['token']
	if (token != 'RNmcnBKCdOZBfs3S7habfT85'):
		return JsonResponse({'text': 'ERROR: Invalid token %s' % token})
	channel_id = request.GET['channel_id']
	try:
		channel = Channel.objects.get(channel_id=channel_id)
	except Channel.DoesNotExist:
		channel = Channel(channel_id=channel_id)
		channel.save() 
	text = request.GET['text']	
	args = text.split(' ')
	if (len(args) < 1 or args[0] == 'help'):
		return showHelp()
	elif (args[0] == 'startGame'):
		return startGame(args, request.GET['user_name'], channel)
	elif (args[0] == 'makeMove'):
		return makeMove(args, request.GET['user_name'], channel)
	elif (args[0] == 'showBoard'):
		return showBoard(channel)
	else:
		return showHelp()

def startGame(args, username, channel):
	usernameX = username # X is the user that ran startGame command

        if (Board.objects.filter(active=True, channel=channel)):
                return generateJsonResponse('There is already an active game in this channel. Please wait til the current game is finished to start a new game. To view current game, use /tictactoe showBoard.', error=True)
	
	if (len(args) < 2):
		return generateJsonResponse('Please specify username of player you would like to play with.', error=True)

	usernameO = args[1] # O is the user that usernameX chose to play with

	# Try to find existing player by username and set position to 1 (X).
	playersWithUsernameX = Player.objects.filter(username=usernameX, channel=None)
	if (len(playersWithUsernameX) > 1):
		playerX = playersWithUsernameX[0]
		playerX.channel = channel
		playerX.save()
	else:
		# Player does not exist yet. Create new player with username.
		playerX = Player(username=usernameX, channel=channel)
		playerX.save()
	
	# Try to find existing player by username and set position to 2 (O).	
	playersWithUsernameO = Player.objects.filter(username=usernameO, channel=None)
	if (len(playersWithUsernameO) > 1):
		playerO = playersWithUsernameO[0]
		playerO.channel = channel
		playerO.save()
	else:
		# Player does not exist yet. Create new player with username.
		playerO = Player(username=usernameO, channel=channel)
		playerO.save()
	
	# Create new board for new game.
        board = Board(active=True, channel=channel, playerX=playerX, playerO=playerO)
        board.save()
	
	return generateJsonResponse('New Tic Tac Toe game between %s and %s!' % (usernameX, usernameO), '%s has next move.%s' % (playerX.username, str(board)))
	
def makeMove(args, username, channel):
	# Fetch board or throw error if does not exist.
	try:
		board = Board.objects.get(active=True, channel=channel)
	except Board.DoesNotExist:	
		return generateJsonResponse('No active games at the moment.', error=True)
		
	if board.game_over:
		return generateJsonResponse('Game is over. Please start a new game.')
	# Fetch player or throw error if does not exist.
	try:
		player = Player.objects.get(username=username, channel=channel)
	except Player.DoesNotExist:
		# Cannot find player.
		return generateJsonResponse('Player %s does not exist.' % username, error=True)
		
	# Determine if player has next turn.
	playerLetter = 1 if player == board.playerX else 2
	nextMove = board.determineWhichPlayerHasNextMove()
	if (playerLetter != nextMove):
		return generateJsonResponse('Player %s is going out of turn.' % username, error=True)
		
	if (len(args) < 2):
		return generateJsonResponse('Please specify which position you would like to choose for your next move. Enter a value between 0 and 8.', error=True)
	# Determine if position is valid.
	try:
		position = int(args[1])
	except ValueError:
		return generateJsonResponse('Invalid position %s. Please enter a position between 0 and 8.' % args[1], error=True)
	if (position < 0 or position > 8):
		return generateJsonResponse('Invalid position %d is out of range. Please enter a position between 0 and 8.' % position, error=True)
	if (board.getLetterAtPosition(position) != 0) :
		return generateJsonResponse('Invalid position %d is already taken. Please enter a position that is empty.' % board.getLetterAtPosition(position), error=True)
	
	# Valid position. Update board config and save.
	board.setLetterAtPosition(playerLetter, position)
	board.save()
	
	# Check if game is over.
	gameOver = False
	winningLetter = board.determineWinner()
	winner = ''
	if (board.isDraw()):
		gameOver = True
		winner = 'Draw'
	elif (winningLetter != 0):
		gameOver = True
		if playerLetter == winningLetter:
			winner = player.username
			
	if gameOver:
		board.game_over = True
		board.active = False
		board.save()

		if (winner == 'Draw'):
			return generateJsonResponse('The game is over and it was a draw.', str(board))
		else:
			return generateJsonResponse('The game is over and %s is the winner.' % winner, str(board))

	else:
		return showBoard(channel)

def showBoard(channel):
	# Fetch board or throw error if does not exist.
        try:
                board = Board.objects.get(active=True, channel=channel)
        except Board.DoesNotExist:
                return generateJsonResponse('No active games at the moment.')

	player = board.playerO if board.determineWhichPlayerHasNextMove() == 2 else board.playerX
	return generateJsonResponse('Active game between %s and %s.' % (board.playerX.username, board.playerO.username), '%s has the next move. %s' % (player.username, str(board)))

def showHelp():
	startGameCommandHelp = '/tictactoe startGame <username> = To start a new game, please specify the username of another user in the channel.'
	makeMoveCommandHelp = '/tictactoe makeMove <position> = If it is your turn, make a move on the board by specifying a position between 0 and 8.\n 0 | 1 | 2\n---------\n 3 | 4 | 5\n---------\n 6 | 7 | 8\n'
	showBoardCommandHelp = '/tictactoe showBoard = To display the current board and which player has the next turn.'
	helpCommandHelp = '/tictactoe help = To show this menu of commands.'
	commands = [startGameCommandHelp, makeMoveCommandHelp, showBoardCommandHelp, helpCommandHelp]
	return generateJsonResponse('Tic Tac Toe Commands List', '\n'.join(commands))

def generateJsonResponse(text, attachmentText='', error=False):
	if error:
		text = 'ERROR: ' + text
	return JsonResponse({'response_type': 'in_channel', 'text': text, 'attachments':[{'text': attachmentText}]})
