"""
List of helper functions to help with parsing code from the engine.jar and
marshalling data into the proper form.
"""

import argparse
import socket
import sys
import random
import math

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator

def convert_hole_cards_to_card_pairs(hand, conv):
    """
    Takes four hole cards in a list, i.e. ['As', '4d', '5s', '8c'] and converts
    it to the 6 possible combinations and formats it into a list of Cards.
    """
    all_pairs = get_all_pairs(hand)
    tuple_pairs = [convert_pbots_hand_to_twohandeval(pair) for pair in all_pairs]
    return convert_list_to_card_list(tuple_pairs)

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

def get_all_pairs(hand):
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

def parse_NEWGAME(data):
    """
    parse the NEWGAME line from engine
    return dictionary of all elements in the line
    """
    info = dict()
    info['yourName'] = data[1]
    info['oppName'] = data[2]
    info['stackSize'] = int(data[3])
    info['bb'] = int(data[4])
    info['numHands'] = int(data[5])
    info['timeBank'] = int(data[6])
    return info

def parse_KEYVALUE(data):
    """
    parse the KEYVALUE line from engine
    return dictionary of all elements in the line
    """
    info = dict()
    info['key'] = data[1]
    info['value'] = data[2]
    return info

def parse_NEWHAND(data):
    """
    parse the NEWHARD line from engine
    return dictionary of all elements in the line
    """
    info = dict()
    info['handId'] = data[1]
    info['button'] = data[2]
    info['holeCards'] = data[3:7]
    info['myBank'] = int(data[7])
    info['otherBank'] = int(data[8])
    info['timeBank'] = float(data[9])
    return info

def parse_HANDOVER(data):
    """
    parse the HANDOVER line from engine
    return dictionary of all elements in the line
    """
    info = dict()
    info['myBankRoll'] = data[1]
    info['opponentBankRoll'] = data[2]
    info['numBoardCards'] = int(data[3])
    info['boardCards'] = data[3:3+numBoardCards]
    info['numLastActions'] = int(data[3+numBoardCards:4+numBoardCards])
    info['timeBank'] = float(data[-1])
    return info

def get_lower_and_upper_bounds(string):
    """
    string: of the form BET:XX:YY or RAISE:XX:YY (not necessarily two digits)
    return: ['BET'/'RAISE', (XX, YY)]
    """

    last_colon = string.rfind(":")
    first_colon = string.find(":")

    if last_colon == -1 or first_colon == -1:
        return "CALL", (0, 0)
    return [string[:first_colon], (int(string[first_colon+1:last_colon]), int(string[last_colon+1:]))]
