import numpy
from collections import defaultdict
import gzip, cPickle
import random
from tqdm import tqdm
# from pokereval.hand_evaluator import HandEvaluator
# from pokereval.card import Card
# import utils

import theano
from theano import tensor as T
from theano.tensor.signal import conv


player1 = 'check_large_a'
player2 = 'check_large_b'

categories = {'high card':1,
			  'one pair':2,
			  'two pairs':3,
			  'three of a kind':4,
			  'straight':5,
			  'flush':6,
			  'full house':7,
			  'four of a kind':8,
			  'straight flush':9,
			  'royal flush':10}

input = T.dmatrix('input')
filter = T.dmatrix('filter')
conv_out = conv.conv2d(input, filter)
f = theano.function([input, filter], conv_out)
# straight_filter = numpy.ones((4,5))
flush_filter = numpy.ones((1,13))
vertical_filter = numpy.ones((4,1))
horizontal_filter = numpy.ones((1,5))


def hand_to_features(hand):
	# hand: list representation of n hands e.g., ['Kc','Ac','6c','7h']
	# returns the output of the filters 
	hand_matrix = string_to_vector(hand)

	column_sums = numpy.sum(hand_matrix, axis=0)
	column_sums[column_sums > 1] = 1
	column_sums = column_sums.reshape((1,14))
	stripped_hand_matrix = numpy.delete(hand_matrix,0,1)

	straight_features = f(column_sums, horizontal_filter)
	straight_features_normalized = numpy.true_divide(straight_features, 5)
	two_three_four_features = f(stripped_hand_matrix, vertical_filter)
	two_three_four_features_normalized = numpy.true_divide(two_three_four_features, 4)
	flush_features = f(stripped_hand_matrix, flush_filter).T
	flush_features_normalized = numpy.true_divide(flush_features, 5)

	return numpy.concatenate((straight_features_normalized, flush_features_normalized, two_three_four_features_normalized), axis = 1)

def table_to_features(hand):
	# hand: list representation of n hands e.g., ['Kc','Ac','6c','7h']
	# returns the output of the filters 
	hand_matrix = string_to_vector(hand)
	# straight_features = f(hand_matrix, straight_filter)

	column_sums = numpy.sum(hand_matrix, axis=0)
	column_sums[column_sums > 1] = 1
	column_sums = column_sums.reshape((1,14))
	stripped_hand_matrix = numpy.delete(hand_matrix,0,1)

	straight_features = f(column_sums, horizontal_filter)
	straight_features_normalized = numpy.true_divide(straight_features, 5)
	two_three_four_features = f(stripped_hand_matrix, vertical_filter)
	two_three_four_features_normalized = numpy.true_divide(two_three_four_features, 4)
	flush_features = f(stripped_hand_matrix, flush_filter).T
	flush_features_normalized = numpy.true_divide(flush_features, 5)
	
	return numpy.concatenate((straight_features_normalized, flush_features_normalized, two_three_four_features_normalized), axis = 1)


def get_conversion():
    """
    create dictionary used in the conversion from hand string to number
    """
    return {r:i for i,r in enumerate('23456789TJQKA', start=2)}

def string_to_vector(hand):
    # hand: list representation of n hands e.g., ['Kc','Ac','6c','7h']
    # return (n+1) matrix (vectorized) of 0's and 1's as numpy array
    conv = get_conversion()

    keyed_by_suit = {'c': [0 for i in range(14)],
                    'h': [0 for i in range(14)],
                    'd': [0 for i in range(14)],
                    's': [0 for i in range(14)]}
    for value,suit in hand:
        value = conv[value]
        if value == 14:
            keyed_by_suit[suit][0] = 1.
        keyed_by_suit[suit][value-1] = 1.

    final_vector = []
    for value in keyed_by_suit.values():
        final_vector.append(value)

    return numpy.asarray(final_vector)


def extract_hands(game):
	"""
	game: string of the whole game (HandLog format)
	return player1 hand as array, player2 hand as array
	"""

	p1_index = game.index('Dealt to '+ player1) + 11 + len(player1)
	p2_index = game.index('Dealt to '+ player2) + 11 + len(player2)

	p1_hand = game[p1_index: p1_index + 11]
	p2_hand = game[p2_index: p2_index + 11]

	return p1_hand.split(), p2_hand.split()


def extract_flop(game):
	"""
	game: string of the whole game (HandLog format)
	return return three table cards after flop as array
	"""
	game = game[game.index('*** FLOP ***'):]
	flop_cards = game[game.index('[')+1:game.index(']')]

	return flop_cards.split()

def extract_turn(game):
	"""
	game: string of the whole game (HandLog format)
	return return four table cards after turn as array
	"""
	game = game[game.index('*** TURN ***'):]
	flop_cards = game[game.index("[")+1:game.index("[")+9].split()
	turn_card = game[game.index("]")+3:game.index("]")+5].split()

	table_cards = flop_cards + turn_card
	return table_cards

def extract_river(game):
	"""
	game: string of the whole game (HandLog format)
	return return four table cards after turn as array
	"""
	game = game[game.index('*** RIVER ***'):]
	flop_cards = game[game.index("[")+1:game.index("[")+12].split()
	turn_card = game[game.index("]")+3:game.index("]")+5].split()

	table_cards = flop_cards + turn_card
	return table_cards

def game_result(game):
	"""
	game: string of the whole game (HandLog format)
	return integer (0 = player1 wins, 1 = player2 wins, 2 = tie)
	"""
	if player1 + " ties for the pot" in game:
		return 2
	elif player1 + " wins the pot" in game:
		return 0
	elif player2 + " wins the pot" in game:
		return 1
	else:
		print "ERROR in player1_wins(game)"
		quit()

def make_data(card_set_type, hand_log_file):
	"""
	card_set_type: 'preflop', 'flop', 'turn', 'river'
	hand_log_file
	creates a [train, valid, test] set and compresses as .pkl.gz 
	"""
	f = open(hand_log_file, 'r')
	full_game = ''
	for line in f:
		full_game += line
	games = full_game.split('\n\n')[:100000]

	data_X = []
	data_Y = []

	complement = {0:1, 1:0, 2:2}

	for game in tqdm(games):

		hand_p1, hand_p2 = extract_hands(game)


		all_pairs_p1 = [[hand_p1[0], hand_p1[1]], [hand_p1[0], hand_p1[2]], [hand_p1[0], hand_p1[3]], [hand_p1[1], hand_p1[2]], [hand_p1[1], hand_p1[3]], [hand_p1[2], hand_p1[3]]]
		all_pairs_p2 = [[hand_p2[0], hand_p2[1]], [hand_p2[0], hand_p2[2]], [hand_p2[0], hand_p2[3]], [hand_p2[1], hand_p2[2]], [hand_p2[1], hand_p2[3]], [hand_p2[2], hand_p2[3]]]

		cards1 = [two_cards + extract_river(game) for two_cards in all_pairs_p1]
		cards2 = [two_cards + extract_river(game) for two_cards in all_pairs_p2]

		features_p1 = numpy.array([hand_to_features(cards).reshape(27,) for cards in cards1])
		features_p2 = numpy.array([hand_to_features(cards).reshape(27,) for cards in cards2])

		features_p1 = numpy.amax(features_p1, axis = 0)
		features_p2 = numpy.amax(features_p2, axis = 0)

		label1 = game_result(game)
		label2 = complement[label1]

		data_X.append(features_p1)
		data_X.append(features_p2)
		data_Y.append(label1)
		data_Y.append(label2)

	random.seed(101)
	random.shuffle(data_X)
	random.seed(101)
	random.shuffle(data_Y)

	data_size = len(data_Y)

	train, valid, test = 0.7, 0.2, 0.1
	break1 = int(train*data_size)
	break2 = break1 + int(valid*data_size)

	train_set = [data_X[:break1], data_Y[:break1]]
	valid_set = [data_X[break1:break2], data_Y[break1:break2]]
	test_set = [data_X[break2:], data_Y[break2:]]

	dataset = [train_set, valid_set, test_set]

	filename = 'custom_filter_dataset_norm_2mil_river' + card_set_type + '.pkl.gz'
	f = gzip.open(filename,'wb')
	cPickle.dump(dataset, f, protocol=2)
	f.close()

if __name__ == '__main__':
	hand_log_file = 'check_large_a_check_large_b.txt'
	make_data('river', hand_log_file)

