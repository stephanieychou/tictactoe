from django.shortcuts import render
from models import Player, Board
from django.http import JsonResponse

def startGame(request):
	# Create new board for new game.
	board = Board()
	board.save()
	
	# Try to find existing player by username and set position to 1 (X).
	try:
		playerX = Player.objects.get(username=request.GET['usernameX'])
		playerX.letter = 1
		playerX.save()
	except Player.DoesNotExist:
		# Player does not exist yet. Create new player with username.
		playerX = Player(username=request.GET['usernameX'], letter=1)
		playerX.save()
	
	# Try to find existing player by username and set position to 2 (O).	
	try:
		playerO = Player.objects.get(username=request.GET['usernameO'])
		playerO.letter = 2
		playerO.save()
	except Player.DoesNotExist:
		# Player does not exist yet. Create new player with username.
		playerO = Player(username=request.GET['usernameO'], letter=2)
		playerO.save()
		
	return JsonResponse({'board_id': board.id})
	
def makeMove(request, board_id):
	# Fetch board or throw error if does not exist.
	try:
		board = Board.objects.get(pk=board_id)
	except Board.DoesNotExist:	
		return JsonResponse({'ERROR': "Board does not exist. id=%s" % board_id})
		
	if board.game_over:
		return JsonResponse({'ERROR': "Game is over. id=%s" % board_id})
	
	# Fetch player or throw error if does not exist.
	username = request.GET['username']
	try:
		player = Player.objects.get(username=username)
	except Player.DoesNotExist:
		# Cannot find player.
		return JsonResponse({'ERROR': "Player does not exist. username=%s" % username})
		
	# Determine if player has next turn.
	if player.letter != board.determineWhichPlayerHasNextMove():
		return JsonResponse({'ERROR': "Player is going out of turn. username=%s" % username})
		
	# Determine if position is valid.
	position = int(request.GET['position'])
	if (position < 0 or position > 8):
		return JsonResponse({'ERROR': "Invalid position, out of range. position=%d" % position})
	if (board.getLetterAtPosition(position) != 0) :
		return JsonResponse({'ERROR': "Invalid position, already taken. username=%d" % board.getLetterAtPosition(position)})
	
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
		board.save()
	
	return JsonResponse({'board_id': board.id, 'board_config': str(board), 'game_over' : game_over, 'winner': winner})
	
