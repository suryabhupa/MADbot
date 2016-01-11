import argparse
import socket
import sys
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
        curr_hand = []
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

            if command == "NEWHAND":
                if PLOT_FLAG == True:
                    MADBot_delta.append(str(data[-3]))
                    otherbot_delta.append(str(data[-2]))
                curr_hand = data[2:6]


            elif command == "GETACTION":
                # Currently CHECK on every move. You'll want to change this.
                s.send("CALL\n")

            elif command == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        print MADBot_delta
        print otherbot_delta
        print "\n".join(MADBot_delta)
        print "=================================================="
        print "\n".join(otherbot_delta)
        s.close()

def parseGETACTION(data):
    potSize = int(data[1])
    numBoardCards = int(data[2])
    boardCards = data[3:3+numBoardCards]
    numLastActions = int(data[3+numBoardCards:4+numBoardCards][0])
    lastActions = data[4+numBoardCards:4+numBoardCards+numLastActions]
    numLegalActions = int(data[4+numBoardCards+numLastActions:5+numBoardCards+numLastActions][0])
    legalActions = data[5+numBoardCards+numLastActions:5+numBoardCards+numLastActions+numLegalActions]
    timebank = float(data[-1])

    return [potSize, numBoardCards, boardCards, numLastActions, lastActions, numLegalActions, legalActions, timebank]

def pb_to_pbots(hand):
    """
    hand has format Ax, where A is # and x is suit
    pokereval_hand has format
    """
    pass


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
