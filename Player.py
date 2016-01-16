import argparse
import socket
import sys
import random
import math
# import matplotlib.pyplot as plt

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator
from utils import *

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
                max_preflop_equity, max_flop_equity = 0, 0 # Flush all equities

            elif command == "NEWHAND":
                if PLOT_FLAG == True:
                    MADBot_delta.append(str(data[-3]))
                    otherbot_delta.append(str(data[-2]))

                info = parse_NEWHAND(data)
                myBank = info['myBank']
                hand = info['holeCards']
                hand_pairs = get_all_pairs(hand)
                # converts engine's format to pokereval's format
                converted_hand_pairs = [(convert_pbots_hand_to_twohandeval(hole[0], conv), convert_pbots_hand_to_twohandeval(hole[1], conv)) for hole in hand_pairs]
                max_preflop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], []) for h in converted_hand_pairs])

            elif command == "GETACTION":
                print 'risk', risk
                info = parse_GETACTION(data)
                rand = random.random()
                if info['numBoardCards'] == 0:
                    l, u = get_lower_and_upper_bounds(info["legalActions"][-1])[1]
                    if myBank > -3000:
                        if max_preflop_equity >= 0.90:
                            s.send("RAISE:" + str(u) + "\n")
                        elif max_preflop_equity >= 0.50:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if rand >= 0.05:
                            s.send("FOLD\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 3:
                    conv_all_cards = []
                    # converts engine's format to pokereval's format
                    converted_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in converted_hand_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        if max_flop_equity >= 0.95:
                            s.send("RAISE:" + str(u) + "\n")
                        elif max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 4:
                    conv_all_cards = []
                    converted_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], converted_board_cards) for h in converted_hand_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        if max_flop_equity >= 0.95:
                            s.send("RAISE:" + str(u) + "\n")
                        elif max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 5:
                    conv_all_cards = []
                    conv_board_cards = convert_list_to_card_list([convert_pbots_hand_to_twohandeval(card, conv) for card in info['boardCards']]) # in Card form
                    max_flop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], conv_board_cards) for h in converted_hand_pairs])
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd != "CALL":
                        if max_flop_equity >= 0.95:
                            s.send("RAISE:" + str(u) + "\n")
                        elif max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if max_flop_equity >= 0.90:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                else:
                    s.send("CALL\n")

            elif command == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")

            elif command == "HANDOVER":
                hand = [""]*4 # Empty the hand
                bankroll = int(data[1])
                # risk = 1
                # if bankroll < 100:
                #     diff = 100 - bankroll
                #     if (float(math.log(diff)/math.log(10))) == 0:
                #         risk = 1
                #     elif bankroll > -50:
                #         risk = 1.0 / (float(math.log(diff)/math.log(10)))**(2)
                #     else:
                #         risk = 1.0 / (float(math.log(diff)/math.log(10)))**2

                # max_preflop_equity, max_flop_equity, max_turn_equity, max_river_equity = 0, 0, 0, 0 # Flush all equities
                max_preflop_equity, max_flop_equity = 0, 0

        # Clean up the socket.
        print MADBot_delta
        print otherbot_delta
        print "\n".join(MADBot_delta)
        print "=================================================="
        print "\n".join(otherbot_delta)
        s.close()

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
