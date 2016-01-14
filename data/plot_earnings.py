import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

players = ['MADbot', 
			'Battlecode', 
			'LeBluff', 
			'Batman', 
			'NeverGF', 
			'0xE29883', 
			'Smokaha',
			'Blackbird',
			'd',
			'ladyshark',
			'GucciPoker',
			'StraightOuttaCam']

current_player = "StraightOuttaCam"
hand_log_dir = "HandLogs/"


##########################################
###	                                   ###
###         PROCESSING GAME 1          ###
###                                    ###
##########################################


game_files = [hand_log_dir+current_player+'_vs_'+player for player in players if player != current_player]

pp = PdfPages(current_player+'_night3_game1.pdf')

for game_file in game_files:
	f = open(game_file, 'r')
	player_2 = game_file.split('_vs_')[1]

	lines = [line.strip() for line in f]
	split_lines = [line.split() for line in lines if len(line)>2]
	hands = [hand for hand in split_lines if hand[0] == "Hand"]
	data = []
	for i,hand in enumerate(hands):
		if i % 2 == 0:
			data.append(int(hand[3][1:-2]))
		else:
			data.append(int(hand[5][1:-1]))

	plt.plot(data)
	plt.title(current_player + " against " + player_2)
	plt.savefig(pp, format = 'pdf')
	f.close()
	plt.clf()

for game_file in game_files:
	f = open(game_file, 'r')
	player_2 = game_file.split('_vs_')[1]

	lines = [line.strip() for line in f]
	split_lines = [line.split() for line in lines if len(line)>2]
	hands = [hand for hand in split_lines if hand[0] == "Hand"]
	data = []
	for i,hand in enumerate(hands):
		if i % 2 == 0:
			data.append(int(hand[3][1:-2]))
		else:
			data.append(int(hand[5][1:-1]))


	plt.plot(data, label=player_2)
	plt.title("all against "+ current_player)
	legend = plt.legend(loc = "lower left",prop={'size':9})
	f.close()


plt.savefig(pp, format = 'pdf')
pp.close()
plt.clf()

##########################################
###	                                   ###
###         PROCESSING GAME 2          ###
###                                    ###
##########################################


game_files = [hand_log_dir+player+'_vs_'+current_player for player in players if player != current_player]

pp2 = PdfPages(current_player+'_night3_game2.pdf')

for game_file in game_files:
	f = open(game_file, 'r')
	player_2 = game_file.split('_vs_')[0][9:]

	lines = [line.strip() for line in f]
	split_lines = [line.split() for line in lines if len(line)>2]
	hands = [hand for hand in split_lines if hand[0] == "Hand"]
	data = []
	for i,hand in enumerate(hands):
		if i % 2 == 1:
			data.append(int(hand[3][1:-2]))
		else:
			data.append(int(hand[5][1:-1]))

	plt.plot(data)
	plt.title(current_player + " against " + player_2)
	plt.savefig(pp2, format = 'pdf')
	f.close()
	plt.clf()

for game_file in game_files:
	f = open(game_file, 'r')
	player_2 = game_file.split('_vs_')[0][9:]

	lines = [line.strip() for line in f]
	split_lines = [line.split() for line in lines if len(line)>2]
	hands = [hand for hand in split_lines if hand[0] == "Hand"]
	data = []
	for i,hand in enumerate(hands):
		if i % 2 == 1:
			data.append(int(hand[3][1:-2]))
		else:
			data.append(int(hand[5][1:-1]))


	plt.plot(data, label=player_2)
	plt.title("all against "+ current_player)
	legend = plt.legend(loc = "lower left",prop={'size':9})
	f.close()

plt.savefig(pp2, format = 'pdf')
pp2.close()



