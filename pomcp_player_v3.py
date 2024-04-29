import random
import math
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

from blackjack.utils import Observation, State

from randomplayer import RandomPlayer

class Particle:
    # 
    def __init__(self, obs: Observation, s: State):
        self.obs = obs
        self.s = s

    @classmethod
    def from_obs(cls, obs):
        return cls(obs, obs.sample_state())
    
    @classmethod
    def from_s(cls, s):
        return cls(s.get_observation(), s)

    

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
    def __init__(self,
                 discount=0.8,
                 depth=0,
                 epsilon=1e-7,
                 explore=7,
                 n_particles=128,
                 reinvigoration=16):

        self.discount = discount
        self.depth = depth
        self.epsilon = epsilon
        self.explore = explore
        self.n_particles = n_particles
        self.reinvigoration = reinvigoration
        self.rollout_policy = RandomPlayer()

    def declare_action(self, valid_actions, hole_card, round_state, ctx):
        obs = Observation(hole_card, round_state)
        at_root = ctx.get('sim_root') is None
        
        if at_root:
            tree = SearchTree()
            ctx['pomcp_root'] = tree
            tree.particles = [Particle.from_obs(obs) for _ in range(self.n_particles)]
        else:
            particles = [part for part in tree.particles if part.obs == obs]
            for _ in range(self.reinvigoration):
                particles.append(Particle.from_obs(obs))
            tree.particles = particles

        for _ in particles:
            particle = random.sample(tree.particles, 1)[0]
            self.simulate(particle, tree, 0, valid_actions)

        best_action = max(self.tree.children.values(), key=lambda x: x.value)
        return best_action.action

    # TODO: FIX ME
    def simulate(self, particle, node, depth, valid_actions): # TODO: double check valid actions is accessible
        if self.discount**depth < self.epsilon:
            return 0
        if depth >= self.max_depth:
            return 0  # Terminal depth reached
        # TODO: Make sure this is valid
        if not node.children:
            node.expand(valid_actions)  # Assuming valid_actions is accessible
            return self.rollout(particle, depth)

        selected_action = max(node.children.values(), key=lambda child: child.value + math.sqrt(2) * node.ucb(child))
        new_particle = Particle.from_game_state(particle.hole_card, particle.community_card)  # Transition function
        reward = self.rollout(new_particle, depth + 1)

        node.visit += 1
        selected_action.visit += 1
        selected_action.value += (reward - selected_action.value) / selected_action.visit

        return reward

    def rollout(self, particle, depth):
        if self.discount**depth < self.epsilon:
            return 0
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