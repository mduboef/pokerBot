import sys
sys.path.insert(0, './pypokerengine/api/')
import game
setup_config = game.setup_config
start_poker = game.start_poker
import time
from argparse import ArgumentParser


""" =========== *Remember to import your agent!!! =========== """
from random_player import RandomPlayer
from raise_player import RaisedPlayer
from tree_player import TreePlayer
from stump_player import StumpPlayer
from evil_player import EvilPlayer
from smart_player import SmartPlayer
from Group11Player import Group11Player
from call_player import CallPlayer
# from smart warrior import SmartWarrior
""" ========================================================= """

""" Example---To run testperf.py with random warrior AI against itself. 

$ python testperf.py -n1 "Random Warrior 1" -a1 RandomPlayer -n2 "Random Warrior 2" -a2 RandomPlayer
"""

def testperf(agent_name1, agent1, agent_name2, agent2, num_games, max_rounds):

	# Init to play 500 games of 1000 rounds
	num_game = num_games
	max_round = max_rounds
	initial_stack = 1000
	smallblind_amount = 10

	# Init pot of players
	agent1_pot = 0
	agent2_pot = 0

	# Setting configuration
	config = setup_config(max_round=max_round, initial_stack=initial_stack, small_blind_amount=smallblind_amount)
	
	# Register players
	config.register_player(name=agent_name1, algorithm=agent1)
	config.register_player(name=agent_name2, algorithm=agent2)
	# config.register_player(name=agent_name1, algorithm=agent1())
	# config.register_player(name=agent_name2, algorithm=agent2())
	

	# Start playing num_game games
	print("\n---------------------------------------\n")
	for game in range(1, num_game+1):
		# print("Game number: ", game)
		game_result = start_poker(config, verbose=0)
		agent1_pot = agent1_pot + game_result['players'][0]['stack']
		agent2_pot = agent2_pot + game_result['players'][1]['stack']

	print("\n After playing {} games of {} rounds, the results are: ".format(num_game, max_round))
	# print("\n Agent 1's final pot: ", agent1_pot)
	print("\n " + agent_name1 + "'s final pot: ", agent1_pot)
	print("\n " + agent_name2 + "'s final pot: ", agent2_pot)

	# print("\n ", game_result)
	# print("\n Random player's final stack: ", game_result['players'][0]['stack'])
	# print("\n " + agent_name + "'s final stack: ", game_result['players'][1]['stack'])

	if (agent1_pot<agent2_pot):
		print("\n Congratulations! " + agent_name2 + " has won.")
	elif(agent1_pot>agent2_pot):
		print("\n Congratulations! " + agent_name1 + " has won.")
		# print("\n Random Player has won!")
	else:
		print("\n It's a draw!") 


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument('-n1', '--agent_name1', help="Name of agent 1", default="Your agent", type=str)
    parser.add_argument('-a1', '--agent1', help="Agent 1", default=EvilPlayer())
    parser.add_argument('-n2', '--agent_name2', help="Name of agent 2", default="Other agent", type=str)
    parser.add_argument('-a2', '--agent2', help="Agent 2", default=RandomPlayer())
    args = parser.parse_args()
    return args.agent_name1, args.agent1, args.agent_name2, args.agent2

if __name__ == '__main__':
	#name1, agent1, name2, agent2 = parse_arguments()
	start = time.time()
	#testperf(name1, agent1, name2, agent2, 3, 100)
	weights_good = [0.3281547950071396, 0.8747720058096283, 0.5847482152699021, 0.7214578804204361, 0.012928631272851085, 0.5746492140001189, 0.4095508933413212, 1, 4]
	weights_new = [0.3060420796952005, 0.7664547714821173, 0.9756685100259848, 0.7221453881090347, 0.8923917436015822, 0.8810826370553613, 0.7652878056675727, 1, 4]
	
	weights_good_II =  [0.3281547950071396, 0.8747720058096283, 0.5847482152699021, 0.7214578804204361, 0.012928631272851085, 0.5746492140001189, 0.4095508933413212, 0, 2]

	testperf("Raised Agent", RaisedPlayer(), "Evil Jr.", Group11Player(), 60, 20000)
	testperf("Random Agent", RandomPlayer(), "Evil Jr.", Group11Player(), 60, 20000)
	testperf("Evil Agent", EvilPlayer(), "Evil Jr.", Group11Player(), 60, 20000)
	testperf("Call Agent", CallPlayer(), "Evil Jr.", Group11Player(), 60, 20000)
	testperf("Smart Agent", SmartPlayer(), "Evil Jr.", Group11Player(), 60, 20000)
	end = time.time()

	print("\n Time taken to play: %.4f seconds" %(end-start))