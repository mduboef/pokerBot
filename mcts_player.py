from pypokerengine.players import BasePokerPlayer
from time import sleep
import pprint
import pickle

from MCTS_poker.populate import SearchTree
import random as rand

class MCTSPlayer(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.nodes = self.load_nodes()
        # print(len(self.nodes))        

    def load_nodes(self):
        with open('search_tree.pkl', 'rb') as f:
            nodes = Pickle.load(f)
        return nodes

    def find_states(self, hole_card_main, community_cards):
        matching_states = {}
        for state, value in self.nodes.items():
            if state.matches(hole_card_main, community_cards):
                matching_states[state] = value
        return matching_states

    def declare_action(self, valid_actions, hole_card, round_state):
        # Check if current observation is a valid state in search tree
        possible_states = self.find_states(hole_card_main=hole_card, community_cards=round_state["community_card"])
        print(possible_states)
        # self.nodes[state]
        # if 
        r = rand.random()
        if r <= 0.5:
            call_action_info = valid_actions[1]
        elif r<= 0.9 and len(valid_actions ) == 3:
            call_action_info = valid_actions[2]
        else:
            call_action_info = valid_actions[0]
        action = call_action_info["action"]
        return action  # action returned here is sent to the poker engine

        return "fold" # action returned here is sent to the poker engine
    
    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return MCTSPlayer()
