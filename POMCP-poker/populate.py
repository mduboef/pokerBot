import random
import math
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.api.emulator import apply_action
from blackjack.utils import Observation, State
from pypokerengine.engine.round_manager import RoundManager
from pypokerengine.engine.hand_evaluator import hand_eval
from pypokerengine.utils.game_state_utils import restore_game_state

from randomplayer import RandomPlayer
asdf
class Particle:
    # TODO: Mason - we need to adjust our state and observation space by adding more features. I think we need information about
    # what the opposing agent has done already (e.g., call, fold, or raise). this should be available in round_state. We need this b/c
    # we need more partial information about the other player otherwise we can't generate a decent probability distribution of observations
    # over states.
    # TODO: mason - add call and raise cointer of opponnent to better infer the belief state.
    def __init__(self, obs: Observation, s: State):
        self.obs = obs
        self.s = s

    @classmethod
    def from_obs(cls, obs):
        """
        Samples a possible state from a uniform distribution given an observation
        """
        return cls(obs, obs.sample_state())
    
    @classmethod
    def from_s(cls, s):
        """
        Gets the observation from the state
        """
        return cls(s.get_observation(), s)

class SearchTree:
    def __init__(self, particles=None, action=None, visit=1, value=0):
        self.particles = particles if particles is not None else []
        self.action = action
        self.visit = visit
        self.value = value
        self.children = {}
        self.actions = [{'action': 'fold'}, {'action': 'call'}, {'action': 'raise'}] # Default valid actions NOTE this will change in rounds

    def expand(self, valid_actions):
        for action in valid_actions:
            # TODO: overwrite possible actions for child node. Check when 
            self.children[action['action']] = SearchTree(action=action['action'])

    def ucb(self, child):
        log_div = math.log(self.visit) / child.visit
        return math.sqrt(log_div)

class POMCP():
    """
    Combines Monte-Carlo belief state updates with PO-UCT Algorithm
    """
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
        self.tree = SearchTree() # This is h
        self.emulator = Emulator()
        self.timeout = 1000
    
    # def search(self, valid_actions, hole_card, round_state):
    #     """
    #     Takes in a belief state and outputs an action
    #     """
    #     obs = Observation(hole_card, round_state)
    #     at_root = self.tree is None
        
    #     if at_root:
    #         tree = SearchTree()
    #         self.tree = tree
    #         self.tree.particles = [Particle.from_obs(obs) for _ in range(self.n_particles)]
    #     else:
    #         particles = [part for part in tree.particles if part.obs == obs]
    #         for _ in range(self.reinvigoration):
    #             # Use particle reinvigoration by adding particles with noise 
    #             # uniform sample from possible states given current observation
    #             particles.append(Particle.from_obs(obs))
    #         self.tree.particles = particles

    #     for _ in particles:
    #         # Take random sample from particles in 
    #         particle = random.sample(self.tree.particles, 1)[0]
    #         self.simulate(particle, tree, 0, valid_actions)

    #     child = max(self.tree.children.values(), key=lambda x: x.value)
    #     self.tree = child
    #     return child.best_action

    # Search module
    # TODO: Finish this
    def search(self):
        particles = self.tree.particles.copy()
        # Repeat Simulations until timeout
        for _ in range(self.timeout):
            if particles == []:
                state = self.State.random_state()  # s ~ I(s_0=s)
            else:
                state = random.choice(particles) # s ~ B(h)
            self.simulate(state, self.tree, 0)
        # Get best action
        action, _ = self.SearchBest(-1, UseUCB=False)
        return action

    def simulate(self, state, tree, depth):
        """
        Simulation performed using the PO-UCT Algorithm
        """
        if (self.discount**depth < self.epsilon) and  depth >= self.max_depth:
            return 0

        # If leaf node
        if not tree.children:
            tree.expand(tree.actions)
            # Lazy Evaluation
            discounted_return = self.rollout(tree, depth)
            # NOTE: Error in POMCP paper. This should be included
            tree.visit += 1
            tree.value = discounted_return
            return discounted_return

        children = filter(lambda child: child.action in tree.actions, tree.children)
        # Upper Confidence Bound (UCB) update
        child = max(children, key=lambda child: child.value + self.explore * tree.ucb(child))
        # Argmax
        action = child.action

        # Black-box step
        # new_s = particle.s.sample(action)
        game_state = restore_game_state(state.round_state)
        new_game_s, messages = RoundManager.apply_action(game_state, action)
        # Convert next game state to State() object
        new_s = State.from_game_state(new_game_s, particle.s.hole_card_main, particle.s.hole_card_op)
        new_part = Particle.from_s(new_s)
        # TODO: Edit Heursitic since rollout gives different rewards (could be off balanced)
        heuristic = hand_eval(new_s.hole_card_main, new_s.community_card) - hand_eval(new_s.hole_card_op, new_s.community_card)
        reward = heuristic + self.discount * self.simulate(new_part, child, depth + 1)
        tree.particles.append(new_part)

        # Tree updates
        tree.visit += 1
        child.visit += 1
        child.value += (reward - child.value) / child.visit
        return reward

    # def rollout(self, particle, depth):
    #     if self.discount**depth < self.epsilon:
    #         return 0
    #     if depth >= self.max_depth:
    #         return 0  # Terminal depth reached
        
    #     # TODO: make rollout_policy random
    #     # Choose action using rollout policy (could be random)
    #     action = self.rollout_policy.policy(particle.obs, {})

    #     # Black-box step
    #     # new_s = particle.s.sample(action)
    #     game_state = restore_game_state(particle.s.round_state)
    #     # TODO: Double check that the next_game_s is the opponents turn to take an action
    #     new_game_opponent, messages = RoundManager.apply_action(game_state, action)
    #     # TODO: get valid actions of opponent
    #     # Calculate valid actions of opponent player
    #     new_round_opponent_state = new_game_opponent['round_state']

    #     # TODO: add conditional for possibility of game ending
    #     new_game_s, messages = RoundManager.apply_action(new_game_opponent, action_opponent)
    #     # Convert next game state to State() object
    #     new_s = State.from_game_state(new_game_s, particle.s.hole_card_main, particle.s.hole_card_op)
    #     new_part = Particle.from_s(new_s)
    #     heuristic = hand_eval(new_s.hole_card_main, new_s.community_card) - hand_eval(new_s.hole_card_op, new_s.community_card)
    #     reward = heuristic + self.discount * self.rollout(new_part, depth + 1)

    #     return reward  # Assuming this is the reward

    def rollout(self, particle, depth):
        if self.discount**depth < self.epsilon:
            return 0
        if depth >= self.max_depth:
            return 0  # Terminal depth reached

        # Black-box step
        game_state = restore_game_state(particle.s.round_state)
        end_game_state, events = self.emulator.run_until_round_finish(game_state)
        reward = events[?] # TODO: Finish and figure out how to get value from game state (USE events)

        return reward  # Assuming this is the reward


if __name__ == '__main__':
  from pypokerengine.api.emulator import Emulator
  num_player = 2
  max_round = 1000
  emulator = Emulator()
  emulator.set_game_rule(num_player, max_round, sb_amount, ante)
  emulator.set_game_rule(player_num=3, max_round=10, small_blind_amount=10, ante_amount=10)

  # 2. Setup GameState object
  players_info = {
      "uuid-1": { "name": "PMOCP", "stack": 1000 },
      "uuid-2": { "name": "RANDOM", "stack": 1000 },
  }
  initial_state = emulator.generate_initial_game_state(players_info)
  game_state, events = emulator.start_new_round(initial_state)