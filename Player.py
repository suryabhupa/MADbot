import argparse
import socket
import sys
import random
import math
import numpy

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator
from tools import *

## Neural Network Imports

sys.path.append('./pdnn')
from models.dnn import DNN
from io_func.model_io import _file2nnet
from io_func import smart_open
import cPickle
import theano
from theano.tensor.signal import conv
import theano.tensor as T


numpy_rng = numpy.random.RandomState(101)

# CODE BELOW NEEDED TO MAKE CONVOLUTIONS WITH THEANO
input = T.dmatrix('input')
filter = T.dmatrix('filter')
conv_out = conv.conv2d(input, filter)
convolution_function = theano.function([input, filter], conv_out)
#################################################

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""

def load_flop_network(nnet_param = 'neural_network/flop_network_params', nnet_cfg = 'neural_network/flop_network_cfg'):
    cfg = cPickle.load(smart_open(nnet_cfg,'r'))
    cfg.init_activation()
    model = DNN(numpy_rng=numpy_rng, cfg = cfg)
    _file2nnet(model.layers, filename = nnet_param)
    get_flop_probs = model.build_extract_feat_function(-1)
    return get_flop_probs

def load_turn_network(nnet_param = 'neural_network/turn_network_params', nnet_cfg = 'neural_network/turn_network_cfg'):
    cfg = cPickle.load(smart_open(nnet_cfg,'r'))
    cfg.init_activation()
    model = DNN(numpy_rng=numpy_rng, cfg = cfg)
    _file2nnet(model.layers, filename = nnet_param)
    get_turn_probs = model.build_extract_feat_function(-1)
    return get_turn_probs


def load_river_network(nnet_param = 'neural_network/river_network_params', nnet_cfg = 'neural_network/river_network_cfg'):
    cfg = cPickle.load(smart_open(nnet_cfg,'r'))
    cfg.init_activation()
    model = DNN(numpy_rng=numpy_rng, cfg = cfg)
    _file2nnet(model.layers, filename = nnet_param)
    get_river_probs = model.build_extract_feat_function(-1)
    return get_river_probs


class Player:
    def run(self, input_socket, get_flop_probs, get_turn_probs, get_river_probs):
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
            data = data.split() # Split data into list
            command = data[0]

            if command == "NEWGAME":
                hand = [""]*4 # Initialize hand to be empty
                risk = 1
                max_preflop_equity, max_flop_equity = 0, 0 # Flush all equities

            elif command == "NEWHAND":
                info = parse_NEWHAND(data)
                myBank = info['myBank']
                if PLOT_FLAG == True:
                    MADBot_delta.append(myBank)
                    otherbot_delta.append(info['otherBank'])

                hand = info['holeCards']
                hand_pairs = get_all_pairs(hand)
                # converts engine's format to pokereval's format
                converted_hand_pairs = [(convert_pbots_hand_to_twohandeval(hole[0], conv), convert_pbots_hand_to_twohandeval(hole[1], conv)) for hole in hand_pairs]
                max_preflop_equity = max([HandEvaluator.evaluate_hand([Card(h[0][0], h[0][1]), Card(h[1][0], h[1][1])], []) for h in converted_hand_pairs])

            elif command == "GETACTION":
                info = parse_GETACTION(data)
                rand = random.random()
                if info['numBoardCards'] == 0:
                    safe = myBank > -3000
                    l, u = get_lower_and_upper_bounds(info["legalActions"][-1])[1]
                    if safe:
                        if info['potSize'] > 50:
                            s.send("CHECK\n")
                        else:
                            if max_preflop_equity > 0.99:
                                if rand >= 0.4:
                                    s.send("RAISE:" + str(l) + "\n")
                            s.send("CALL\n")
                    else:
                        if max_preflop_equity >= 0.99 and info['potSize'] < 50:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 3:
                    table_cards = info['boardCards']
                    features = get_omaha_features(hand, table_cards, convolution_function, play = 'flop')
                    probs = get_turn_probs(features.reshape(1,27))[0]
                    prob_winning = probs[0]
                    print "###### FLOP #####"
                    print hand
                    print table_cards
                    print prob_winning
                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd == 'BET':
                        if prob_winning >= 0.8:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.7:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.6:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                    elif cmd == 'RAISE':
                        if prob_winning >= 0.85:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.75:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.7:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if prob_winning >= 0.7:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 4:
                    table_cards = info['boardCards']
                    features = get_omaha_features(hand, table_cards, convolution_function, play = 'turn')
                    probs = get_turn_probs(features.reshape(1,27))[0]
                    prob_winning = probs[0]
                    print "###### TURN #####"
                    print hand
                    print table_cards
                    print prob_winning

                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    if cmd == 'BET':
                        if prob_winning >= 0.8:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.7:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.5:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                    elif cmd == 'RAISE':
                        if prob_winning >= 0.9:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.85:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.7:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if prob_winning >= 0.7:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                elif info['numBoardCards'] == 5:
                    table_cards = info['boardCards']
                    features = get_omaha_features(hand, table_cards, convolution_function, play = 'river')
                    probs = get_turn_probs(features.reshape(1,27))[0]
                    prob_winning = probs[0]
                    print "###### RIVER #####"
                    print hand
                    print table_cards
                    print prob_winning

                    cmd, (l, u) = get_lower_and_upper_bounds(info["legalActions"][-1])
                    print cmd
                    if cmd == 'BET':
                        if prob_winning >= 0.75:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.7:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.6:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")

                    elif cmd == 'RAISE':
                        if prob_winning >= 0.95:
                            if rand > 0.3:
                                s.send(cmd+":" + str(u) + "\n")
                            else:
                                s.send(cmd+":" + str(l) + "\n")
                        elif prob_winning >= 0.8:
                            if rand < 0.2:
                                s.send(cmd+":" + str(u) + "\n")
                            elif rand < 0.6:
                                s.send(cmd+":" + str(l) + "\n")
                            else:
                                s.send("CALL\n")
                        elif prob_winning >= 0.7:
                            s.send("CALL\n")
                        else:
                            s.send("CHECK\n")
                    else:
                        if prob_winning >= 0.7:
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
        # print "\n".join(MADBot_delta)
        # print "=================================================="
        # print "\n".join(otherbot_delta)
        s.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    PLOT_FLAG = True # Plots the results of the MADBot and other player.
    MADBot_delta = []
    otherbot_delta = []

    get_flop_probs, get_turn_probs, get_river_probs = load_flop_network(), load_turn_network(), load_river_network()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s,get_flop_probs, get_turn_probs, get_river_probs)
