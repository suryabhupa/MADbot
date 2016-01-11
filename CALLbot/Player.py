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

            s.send("CALL\n")

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
