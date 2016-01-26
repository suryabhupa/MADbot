from collections import defaultdict
import re
import numpy as np
import matplotlib.pyplot as plt
x = []
y = []
my_x = []
my_y = []
players = ['0xE29883',
			'Baker3W',
			'Batman',
			'Battlecode',
			'Cambot',
			'Checkmate', 
			'Evangelion', 
			'Frendan',
			'GucciPoker',
			'HalstonTaylor', 
			'IHTFG',
			'kkzpokerbot',
			# 'ladyshark',
			'Learning',
			'LeBluff',
			# 'MADbot',
			'NeverGF',
			'OGRoomies',
			'Pokermon',
			'QuantumPoker',
			'Ripka',
			# 'Smokaha',
			'StraightOuttaCam',
			'TheLuck']

players = ['mini']


def get_game_id(game):
	game = game[:game.index(',')]
	return int(game[6:])

def get_preflop_opening(game, little_blind_player, big_blind_player):
	game = game[game.index('Dealt to ' + big_blind_player):].split('\n')
	move = game[1]
	move = move[len(little_blind_player)+1:]
	return move

for playa in players:
	player1 = playa
	player2 = 'Neural'
	# gamefile = 'HandLongsMini/'+player1+'_vs_'+player2
	gamefile = '../../mini_MADbot.txt'


	f = open(gamefile, 'r')

	full_game = ''

	# lol to get rid of the header line
	for line in f:
		break
	# to create a list of full games
	for line in f:
		full_game += line
	games = full_game.split('\n\n')[:-1]

	# distribution of player1's pre-flop when little blind
	p1_pre_flop = defaultdict(int)

	# distribution of player2's pre-flop when little blind
	p2_pre_flop = defaultdict(int)

	for game in games:
		if get_game_id(game)%2 == 0:
			p2_pre_flop[get_preflop_opening(game, player2, player1)] += 1
		elif get_game_id(game)%2 == 1:
			p1_pre_flop[get_preflop_opening(game, player1, player2)] += 1


	p1_checks = []
	p2_checks = []
	p1_calls = []
	p2_calls = []
	p1_raises = []
	p2_raises = []
	p1_folds = []
	p2_folds = []
	p1_bets = []
	p2_bets = []

	p1_agression = []
	p2_agression = []

	rounds_before_p1_folds = []
	rounds_before_p2_folds = []

	for game in games:
		if "*** FLOP ***" in game:
			game = game[game.index('*** FLOP ***'):]
			num_checks_p1 = len([m.start() for m in re.finditer(player1+' checks', game)])
			num_checks_p2 = len([m.start() for m in re.finditer(player2+' checks', game)])

			num_calls_p1 = len([m.start() for m in re.finditer(player1+' calls', game)])
			num_calls_p2 = len([m.start() for m in re.finditer(player2+' calls', game)])

			num_raises_p1 = len([m.start() for m in re.finditer(player1+' raises', game)])
			num_raises_p2 = len([m.start() for m in re.finditer(player2+' raises', game)])

			num_folds_p1 = len([m.start() for m in re.finditer(player1+' folds', game)])
			num_folds_p2 = len([m.start() for m in re.finditer(player2+' folds', game)])

			num_bets_p1 = len([m.start() for m in re.finditer(player1+' bets', game)])
			num_bets_p2 = len([m.start() for m in re.finditer(player2+' bets', game)])

			total_actions_p1 = num_checks_p1 + num_calls_p1 + num_raises_p1 + num_folds_p1 + num_bets_p1
			total_actions_p2 = num_checks_p2 + num_calls_p2 + num_raises_p2 + num_folds_p2 + num_bets_p2

			p1_checks.append(num_checks_p1)
			p2_checks.append(num_checks_p2)

			p1_calls.append(num_calls_p1)
			p2_calls.append(num_calls_p2)

			p1_raises.append(num_raises_p1)
			p2_raises.append(num_raises_p2)

			p1_folds.append(num_folds_p1)
			p2_folds.append(num_folds_p2)

			p1_folds.append(num_folds_p1)
			p2_folds.append(num_folds_p2)

			p1_agression.append(float((num_bets_p1+num_raises_p1))/total_actions_p1)
			p2_agression.append(float((num_bets_p2+num_raises_p2))/total_actions_p2)

			if player1 + ' folds' in game:
				rounds_before_p1_folds.append(total_actions_p1+total_actions_p2)
			if player2 + ' folds' in game:
				rounds_before_p2_folds.append(total_actions_p1+total_actions_p2)


	y.append(float(sum(p1_agression))/len(p1_agression))
	x.append(float(sum(rounds_before_p1_folds))/len(rounds_before_p1_folds))

	try:
		my_y.append(float(sum(p2_agression))/len(p2_agression))
		my_x.append(float(sum(rounds_before_p2_folds))/len(rounds_before_p2_folds))
	except:
		print game[-1][:50]
		continue
	# print float(sum(p1_agression))/len(p1_agression), float(sum(rounds_before_p1_folds))/len(rounds_before_p1_folds)

	# print float(sum(p2_agression))/len(p2_agression), float(sum(rounds_before_p2_folds))/len(rounds_before_p2_folds)

print float(sum(my_x))/len(my_x)
print float(sum(my_y))/len(my_y)
print x
print y
# labels = [-1,1,1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,1,1,1]
# plt.scatter(x, y, c=labels, alpha=0.5)
# plt.show()



