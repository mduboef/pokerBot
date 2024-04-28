import random
import math
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

class Particle:
    def __init__(self, hole_card, community_card):
        self.hole_card = hole_card
        self.community_card = community_card

    @classmethod
    def from_game_state(cls, hole_card, community_card):
        return cls(hole_card, community_card)

class SearchTree:
    def __init__(self, particles=None, action=None, visit=1, value=0):
        self.particles = particles if particles is not None else []
        self.action = action
        self.visit = visit
        self.value = value
        self.children = {}

    def expand(self, valid_actions):
        for action in valid_actions:
            self.children[action['action']] = SearchTree(action=action['action'])

    def ucb(self, child):
        log_div = math.log(self.visit) / child.visit
        return math.sqrt(log_div)

class POMCPPlayer(BasePokerPlayer):
    def __init__(self, n_particles=100, max_depth=10):
        self.n_particles = n_particles
        self.max_depth = max_depth
        self.tree = None

    def declare_action(self, valid_actions, hole_card, round_state):
        self.tree = SearchTree()
        self.tree.expand(valid_actions)

        community_cards = round_state['community_card']
        particles = [Particle.from_game_state(hole_card, community_cards) for _ in range(self.n_particles)]

        for particle in particles:
            self.simulate(particle, self.tree, 0, valid_actions)

        best_action = max(self.tree.children.values(), key=lambda x: x.value)
        return best_action.action, best_action.action['amount']

    def simulate(self, particle, node, depth, valid_actions): # TODO: double check valid actions is accessible
        if depth >= self.max_depth:
            return 0  # Terminal depth reached

        if not node.children:
            node.expand(valid_actions)  # Assuming valid_actions is accessible

        selected_action = max(node.children.values(), key=lambda child: child.value + math.sqrt(2) * node.ucb(child))
        new_particle = Particle.from_game_state(particle.hole_card, particle.community_card)  # Transition function
        reward = self.rollout(new_particle, depth + 1)

        node.visit += 1
        selected_action.visit += 1
        selected_action.value += (reward - selected_action.value) / selected_action.visit

        return reward

    def rollout(self, particle, depth):
        if depth >= self.max_depth:
            return 0  # Terminal depth reached

        current_win_rate = estimate_hole_card_win_rate(nb_simulation=100, nb_player=2, hole_card=gen_cards(particle.hole_card), community_card=gen_cards(particle.community_card))
        return current_win_rate  # Assuming this is the reward

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
    return POMCPPlayer()