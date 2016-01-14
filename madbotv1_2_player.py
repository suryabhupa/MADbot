import argparse
import socket
import sys
import random
import math
# import matplotlib.pyplot as plt

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        conv = create_pbots_hand_to_twohandeval_dict()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            print data

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            data = data.split() # Split data into list
            command = data[0]

            if command == "NEWGAME":
                hand = [""]*4 # Initialize hand to be empty
                risk = 1
                max_preflop_equity, max_flop_equity, max_turn_equity, max_river_equity = 0, 0, 0, 0 # Flush all equities

            elif command == "NEWHAND":
                if PLOT_FLAG == True: # Logging
                    MADBot_delta.append(str(data[-3]))
                    otherbot_delta.append(str(data[-2]))
                hand = data[3:7]
                two_pairs = return_pairs(hand)
                convs_two_pairs = [(convert_pbots_hand_to_twohandeval(hole[0], conv), convert_pbots_hand_to_twohandeval(hole[1], conv)) for hole in two_pairs]
                max_preflop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], []) for h in convs_two_pairs])

            elif command == "GETACTION":
                # Currently CHECK on every move. You'll want to change this.
                print 'risk', risk
                info = parse_GETACTION(data)
                if info['numBoardCards'] == 0:
                    l, u = get_lower_and_upper_bounds(info["legalActions"][-1])[1]
                    if max_preflop_equity >= 0.99:
                        s.send("RAISE:" + str(u) + "\n")
                    elif max_preflop_equity >= 0.97:
                        avg = int((u+l)/2)
                        s.send("RAISE:" + str(avg) + "\n")
                    elif max_preflop_equity >= 0.95:
                        s.send("RAISE:" + str(l) + "\n")
                    else:
                        s.send("CALL\n")

                elif info['numBoardCards'] == 3:
                    conv_all_cards = []
                    conv_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], conv_board_cards) for h in convs_two_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        rand = random.random()
                        if risk < 0.1:
                            if (rand >= 0.05):
                                s.send("FOLD\n")
                            else:
                                s.send("CHECK\n")
                        else:
                            if max_flop_equity >= 0.90:
                                if (rand < 0.05):
                                    s.send("CHECK\n")
                                elif (risk < 0.2):
                                    s.send("CALL\n")
                                else:
                                    s.send(cmd + ":" + str(u) + "\n")
                            elif max_flop_equity >= 0.80:
                                if (risk < 0.2):
                                    if (rand < 0.1):
                                        s.send("CALL\n")
                                    else:
                                        s.send("CHECK\n")
                                elif (rand < 0.10):
                                    s.send("CHECK\n")
                                else:
                                    avg = int((u+l)/2)
                                    s.send(cmd + ":" + str(avg) + "\n")
                            elif max_flop_equity >= 0.60:
                                if (rand < 0.15) or risk < 0.2:
                                    s.send("CHECK\n")
                                else:
                                    s.send(cmd + ":" + str(l) + "\n")
                            else:
                                if (rand < 0.05):
                                    s.send("CALL\n")
                                else:
                                    s.send("FOLD\n")
                    else:
                        s.send("CALL\n")

                elif info['numBoardCards'] == 4:
                    conv_all_cards = []
                    conv_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], conv_board_cards) for h in convs_two_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        rand = random.random()
                        if risk < 0.1:
                            if (rand >= 0.05):
                                s.send("FOLD\n")
                            else:
                                s.send("CHECK\n")
                        else:
                            if max_flop_equity >= 0.95:
                                if (rand < 0.05):
                                    s.send("CHECK\n")
                                elif (risk < 0.01):
                                    s.send("CALL\n")
                                else:
                                    s.send(cmd + ":" + str(u) + "\n")
                            elif max_flop_equity >= 0.85:
                                if (risk < 0.2):
                                    if (rand < 0.1):
                                        s.send("CALL\n")
                                    else:
                                        s.send("CHECK\n")
                                elif (rand < 0.10):
                                    s.send("CHECK\n")
                                else:
                                    avg = int((u+l)/2)
                                    s.send(cmd + ":" + str(avg) + "\n")
                            elif max_flop_equity >= 0.50:
                                if (rand < 0.15) or risk < 0.2:
                                    s.send("CHECK\n")
                                else:
                                    s.send("CHECK\n")
                            else:
                                if (rand < 0.05):
                                    s.send("CALL\n")
                                else:
                                    s.send("FOLD\n")
                    else:
                        s.send("CALL\n")

                elif info['numBoardCards'] == 5:
                    conv_all_cards = []
                    conv_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], conv_board_cards) for h in convs_two_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        rand = random.random()
                        if risk < 0.1:
                            if (rand >= 0.05):
                                s.send("FOLD\n")
                            else:
                                s.send("CHECK\n")
                        else:
                            if max_flop_equity >= 0.95:
                                if (rand < 0.05):
                                    s.send("CHECK\n")
                                elif (risk < 0.01):
                                    s.send("CALL\n")
                                else:
                                    s.send(cmd + ":" + str(u) + "\n")
                            elif max_flop_equity >= 0.85:
                                if (risk < 0.2):
                                    if (rand < 0.1):
                                        s.send("CALL\n")
                                    else:
                                        s.send("CHECK\n")
                                elif (rand < 0.10):
                                    s.send("CHECK\n")
                                else:
                                    avg = int((u+l)/2)
                                    s.send(cmd + ":" + str(avg) + "\n")
                            elif max_flop_equity >= 0.50:
                                if (rand < 0.15) or risk < 0.2:
                                    s.send("CHECK\n")
                                else:
                                    s.send("CHECK\n")
                            else:
                                if (rand < 0.05):
                                    s.send("CALL\n")
                                else:
                                    s.send("FOLD\n")
                    else:
                            s.send("CALL\n")
                else:
                    s.send("CALL\n")

            elif command == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")

            elif command == "HANDOVER":
                hand = [""]*4 # Empty the hand
                bankroll = int(data[1])
                risk = 1
                if bankroll < 100:
                    diff = 100 - bankroll
                    if (float(math.log(diff)/math.log(10))) == 0:
                        risk = 1
                    elif bankroll > -50:
                        risk = 1.0 / (float(math.log(diff)/math.log(10)))**(2)
                    else:
                        risk = 1.0 / (float(math.log(diff)/math.log(10)))**2

                max_preflop_equity, max_flop_equity, max_turn_equity, max_river_equity = 0, 0, 0, 0 # Flush all equities

        # Clean up the socket.
        print MADBot_delta
        print otherbot_delta
        print "\n".join(MADBot_delta)
        print "=================================================="
        print "\n".join(otherbot_delta)
        s.close()

def convert_list_to_card_list(lst):
    """
    lst has entries like (N, M), and will convert it to Card(N, M)
    """

    card_lst = []
    for i in lst:
        card_lst.append(Card(i[0], i[1]))

    return card_lst

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

def convert_pbots_hand_to_twohandeval(hand, conv):
    """
    hand: format Ax, where A is # and x is suit
    pokereval_hand: format tuple (N, M) where N is number and M is suit,
        where N ranges from 2-A and M ranges from 1-4
        1: spades
        2: hearts
        3: diamonds
        4: clubs
    """
    return (conv[hand[0]], conv[hand[1]])

def return_pairs(hand):
    """
    hand: list of size 4, each element is a card
    Return: returns all (4 choose 2) pairs of the original hand to compute 2-card preflop equities
    """
    return [(hand[0], hand[1]), (hand[0], hand[2]), (hand[0], hand[3]), (hand[1], hand[2]), (hand[1], hand[3]), (hand[2], hand[3])]

def parse_GETACTION(data):
    """
    parse the GETACTION line from engine
    return dictionary of all elements in the line
    """
    info = dict()
    info['potSize'] = int(data[1])
    info['numBoardCards'] = int(data[2])
    info['boardCards'] = data[3:3+info['numBoardCards']]
    info['numLastActions'] = int(data[3+info['numBoardCards']:4+info['numBoardCards']][0])
    info['lastActions'] = data[4+info['numBoardCards']:4+info['numBoardCards']+info['numLastActions']]
    info['numLegalActions'] = int(data[4+info['numBoardCards']+info['numLastActions']:5+info['numBoardCards']+info['numLastActions']][0])
    info['legalActions'] = data[5+info['numBoardCards']+info['numLastActions']:5+info['numBoardCards']+info['numLastActions']+info['numLegalActions']]
    info['timebank'] = float(data[-1])
    return info

def get_lower_and_upper_bounds(string):
    """
    string: of the form BET:XX:YY or RAISE:XX:YY (not necessarily two digits)
    return: (XX, YY)
    """

    last_colon = string.rfind(":")
    first_colon = string.find(":")

    if last_colon == -1 or first_colon == -1:
        return "CALL", (0, 0)
    return [string[:first_colon], (int(string[first_colon+1:last_colon]), int(string[last_colon+1:]))]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    PLOT_FLAG = True # Plots the results of the MADBot and other player.
    MADBot_delta = []
    otherbot_delta = []


    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
