from collections import defaultdict
from pokereval.card import Card
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from pokereval.hand_evaluator import HandEvaluator

def main():
    game_file = 'HandLogs4/MADbot_vs_StraightOuttaCam'
    player_1 = game_file.split('_vs_')[0][10:]
    player_2 = game_file.split('_vs_')[1]

    f = open(game_file, 'r')
    lines = [line for line in f][1:]

    full_game_string = ''
    for line in lines:
        full_game_string += line

    game_buckets = full_game_string.split('\n\n')[:-1]
    categories = defaultdict(list)
    winner = defaultdict(list)

    # Buckets all of the games into one of 6 categories:
    # (1)full_game (players show their cards)
    # Player 1 folds ((2)fold_after_river, (3)fold_after_turn, (4)fold_after_flop, (5)fold_before_flop)
    # (2)opponent_folds (player 2 folds at some point in the game)
    for game in game_buckets:
        if player_1 + " shows" in game:
            categories['full_game'] += [game]
        elif player_1 + " folds" in game:
            if "*** RIVER ***" in game:
                categories['fold_after_river'] += [game]
            elif "*** TURN ***" in game:
                categories['fold_after_turn'] += [game]
            elif "*** FLOP ***" in game:
                categories['fold_after_flop'] += [game]
            else:
                categories['fold_before_flop'] += [game]
        elif player_2 + " folds" in game:
            categories['opponent_folds'] += [game]
        if player_1 + " wins the pot" in game:
            winner[player_1].append(game)
        else:
            winner[player_2].append(game)


    preflops = []
    p1_equities = []
    for game in winner[player_1]:
        if game not in categories['full_game']:
            continue
        player_1_hand, player_2_hand = get_players_hands(game, player_1, player_2)
        
        # Getting pre-flop statistics
        # max_preflop = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], []) for h in player_1_hand])
        # preflops.append(max_preflop)

        # Getting post-flop statistics

        game = game[game.index("*** RIVER ***"):]
        table_cards = game[game.index("[")+1:game.index("[")+12].split()
        table_cards_last = game[game.index("]")+3:game.index("]")+5].split()
        # table_cards = game[game.index("[")+1:game.index("[")+9].split()
        # table_cards_last = game[game.index("]")+3:game.index("]")+5].split()
        table_cards = table_cards + table_cards_last


        conv = create_pbots_hand_to_twohandeval_dict()
        converted_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card) for card in table_cards]) # in pbotseval form
        max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in player_1_hand])
        # if max_flop_equity > 0.99:
        #     print table_cards
        #     print player_1_hand
        #     print [HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in player_1_hand]
        #     print player_2_hand
        #     print [HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in player_2_hand]
        p1_equities.append(max_flop_equity)


    print len(p1_equities)
    n, bins, patches = plt.hist(p1_equities, 100, normed=1, facecolor='green', alpha=0.75)
    plt.title('We won post river')
    plt.show()



    # p1_equities = []
    # p2_equities = []
    # player_1_wins,player_2_wins,ties = 0,0,0

    # for key,value in categories.items():
    #     print key,len(value)

    # for game in categories['full_game']:
    #     player_1_hand, player_2_hand = get_players_hands(game, player_1, player_2)
    #     game = game[game.index("*** RIVER ***"):]
    #     table_cards = game[game.index("[")+1:game.index("[")+12].split()
    #     table_cards_last = game[game.index("]")+3:game.index("]")+5].split()
    #     table_cards = table_cards + table_cards_last
    #     # print "Table card: ",table_cards

    #     conv = create_pbots_hand_to_twohandeval_dict()        
    #     converted_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card) for card in table_cards]) # in pbotseval form

    #     max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in player_1_hand])
    #     p1_equities.append(max_flop_equity)
    #     max_flop_equity2 = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in player_2_hand])
    #     p2_equities.append(max_flop_equity2)
        

    #     if player_1 + " wins the pot" in game:
    #         player_1_wins += 1
    #     elif player_2 + " wins the pot" in game:
    #         player_2_wins += 1
    #     elif player_1 + " ties for the pot" in game:
    #         ties += 1

    # print sum(p1_equities)/float(len(p1_equities))
    # print sum(p2_equities)/float(len(p2_equities))

    # print player_1_wins
    # print player_2_wins
    # print ties

        # print max_flop_equity
        # print max_flop_equity2


def get_players_hands(game, player_1, player_2):
    """
    game: one game represented as a string
    Return: all pair of hands in both players after conv
    """
    index_1 = game.index('Dealt to ' + player_1)
    player_1_hand = game[index_1+len(player_1) + 11: index_1+len(player_1)+ 23].split()
    # print "Player 1 hand: ", player_1_hand
    player_1_hand = [convert_pbots_hand_to_twohandeval(hand) for hand in player_1_hand]
    player_1_hand = [(card[0],card[1]) for card in player_1_hand]

    index_2 = game.index('Dealt to ' + player_2)
    player_2_hand = game[index_2+len(player_2) + 11: index_2+len(player_2)+ 23].split()
    # print "Player 2 hand: ", player_2_hand
    player_2_hand = [convert_pbots_hand_to_twohandeval(hand) for hand in player_2_hand]
    player_2_hand = [(card[0],card[1]) for card in player_2_hand]

    p1_all_pairs = get_all_pairs(player_1_hand)
    p2_all_pairs = get_all_pairs(player_2_hand)

    return p1_all_pairs, p2_all_pairs


def get_post_river_cards(game):
    """
    game: one game represented as a string
    Return: 
    """
    return 0

def get_all_pairs(hand):
    """
    hand: list of size 4, each element is a card
    Return: returns all (4 choose 2) pairs of the original hand to compute 2-card preflop equities
    """
    return [(hand[0], hand[1]), (hand[0], hand[2]), (hand[0], hand[3]), (hand[1], hand[2]), (hand[1], hand[3]), (hand[2], hand[3])]

def convert_pbots_hand_to_twohandeval(hand):
    """
    hand: format Ax, where A is # and x is suit
    pokereval_hand: format tuple (N, M) where N is number and M is suit,
        where N ranges from 2-A and M ranges from 1-4
        1: spades
        2: hearts
        3: diamonds
        4: clubs
    """
    conv = create_pbots_hand_to_twohandeval_dict()
    return (conv[hand[0]], conv[hand[1]])

def create_pbots_hand_to_twohandeval_dict():
    """
    create dictionary used in the conversion to be used by pokerval library;
    see convert_pbots_hand_to_twohandeval(hand) for details about conversions
    """
    conv = dict()
    conv["1"] = 1
    conv["2"] = 2
    conv["3"] = 3
    conv["4"] = 4
    conv["5"] = 5
    conv["6"] = 6
    conv["7"] = 7
    conv["8"] = 8
    conv["9"] = 9
    conv["T"] = 10
    conv["J"] = 11
    conv["Q"] = 12
    conv["K"] = 13
    conv["A"] = 14
    conv["s"] = 1
    conv["h"] = 2
    conv["d"] = 3
    conv["c"] = 4

    return conv

def convert_list_to_card_list(lst):
    """
    lst has entries like (N, M), and will convert it to Card(N, M)
    """

    card_lst = []
    for i in lst:
        card_lst.append(Card(i[0], i[1]))

    return card_lst

if __name__ == '__main__':
    main()
