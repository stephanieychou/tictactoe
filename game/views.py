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
	if (args[0] == 'startGame'):
		return startGame(args, request.GET['user_name'], channel)
	elif (args[0] == 'makeMove'):
		return makeMove(args, request.GET['user_name'], channel)
	elif (args[0] == 'showBoard'):
		return showBoard(channel)

def startGame(args, username, channel):
	usernameX = username # X is the user that ran startGame command
	usernameO = args[1] # O is the user that usernameX chose to play with

	# Create new board for new game.
	board = Board(active=True, channel=channel)
	board.save()
	
	# Try to find existing player by username and set position to 1 (X).
	try:
		playerX = Player.objects.get(username=usernameX, channel=None)
		playerX.letter = 1
		playerX.channel = channel
		playerX.save()
	except Player.DoesNotExist:
		# Player does not exist yet. Create new player with username.
		playerX = Player(username=usernameX, letter=1, channel=channel)
		playerX.save()
	
	# Try to find existing player by username and set position to 2 (O).	
	try:
		playerO = Player.objects.get(username=usernameO, channel=None)
		playerO.letter = 2
		playerO.channel = channel
		playerO.save()
	except Player.DoesNotExist:
		# Player does not exist yet. Create new player with username.
		playerO = Player(username=usernameO, letter=2, channel=channel)
		playerO.save()
		

	return JsonResponse({'response_type': 'in_channel','response_type': 'in_channel','text': 'New Tic Tac Toe game between %s and %s' % (usernameX, usernameO), 'attachments': [{'text': "%s\nPlayer X (%s) to make next move." % (str(board), playerX.username)}]})
	
def makeMove(args, username, channel):
	# Fetch board or throw error if does not exist.
	try:
		board = Board.objects.get(active=True, channel=channel)
	except Board.DoesNotExist:	
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: No active games at the moment."})
		
	if board.game_over:
		return JsonResponse({'response_type': 'in_channel','text': "Game is over. Please start a new game."})
	# Fetch player or throw error if does not exist.
	try:
		player = Player.objects.get(username=username, channel=channel)
	except Player.DoesNotExist:
		# Cannot find player.
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: Player %s does not exist." % username})
		
	# Determine if player has next turn.
	if player.letter != board.determineWhichPlayerHasNextMove():
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: Player %s is going out of turn." % username})
		
	# Determine if position is valid.
	try:
		position = int(args[1])
	except ValueError:
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: Invalid position %s. Please enter a position between 0 and 8." % args[1]})
	if (position < 0 or position > 8):
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: Invalid position %d is out of range. Please enter a position between 0 and 8." % position})
	if (board.getLetterAtPosition(position) != 0) :
		return JsonResponse({'response_type': 'in_channel','text': "ERROR: Invalid position %d is already taken. Please enter a position that is empty." % board.getLetterAtPosition(position)})
	
	# Valid position. Update board config and save.
	board.setLetterAtPosition(player.letter, position)
	board.save()
	
	# Check if game is over.
	game_over = False
	winningLetter = board.determineWinner()
	winner = ""
	if (board.isDraw()):
		game_over = True
		winner = "Draw"
	elif (winningLetter != 0):
		game_over = True
		if player.letter == winningLetter:
			winner = player.username
			
	if game_over:
		board.game_over = True
		board.active = False
		board.save()

		playerX = Player.objects.get(letter=1, channel=channel)
		playerX.letter = 0
		playerX.save()

		playerO = Player.objects.get(letter=2, channel=channel)
		playerO.letter = 0
		playerO.save()

	if (game_over):
		if (winner == "Draw"):
			return JsonResponse({'response_type': 'in_channel','text': 'The game is over and it was a draw.', 'attachments':[{'text': str(board)}]})
		else:
			return JsonResponse({'response_type': 'in_channel','text': 'The game is over and %s is the winner.' % winner, 'attachments':[{'text': str(board)}]})

	else:
		nextPlayer = Player.objects.get(letter=board.determineWhichPlayerHasNextMove(), channel=channel)
		return JsonResponse({'response_type': 'in_channel','text': '%s has the next move.' % nextPlayer.username, 'attachments':[{'text': str(board)}]}) 

def showBoard(channel):
	# Fetch board or throw error if does not exist.
        try:
                board = Board.objects.get(active=True, channel=channel)
        except Board.DoesNotExist:
                return generateJsonResponse("No active games at the moment.")

	try:
		player = Player.objects.get(letter = board.determineWhichPlayerHasNextMove(), channel=channel)
	except Player.DoesNotExist:
		return JsonResponse({})

	return generateJsonResponse('%s has the next move.' % player.username, str(board))

def generateJsonResponse(text, attachmentText="", error=False):
	if error:
		text = 'ERROR: ' + text
	return JsonResponse({'response_type': 'in_channel', 'text': text, 'attachments':[{'text': attachmentText}]})
