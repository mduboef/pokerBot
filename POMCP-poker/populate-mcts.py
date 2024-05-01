import random
import math
import sys

sys.path.insert(0, './')
from pypokerengine.engine.table import Table
from pypokerengine.engine.seats import Seats
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
# from pypokerengine.api.emulator import apply_action
from blackjack.utils import Observation, State, from_state_action_to_state, get_valid_actions
from pypokerengine.engine.round_manager import RoundManager
# from pypokerengine.engine.hand_evaluator import eval_hand
from pypokerengine.utils.game_state_utils import restore_game_state
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.api.emulator import Emulator
from randomplayer import RandomPlayer

class SearchTree:
    def __init__(self, player = None, state=None, action=None, visit=0, value=0, parent=None):
        self.player: str = player    # "main" or "opp"
        self.action: str = action    # Action by the opponent that was taken in parent
        self.parent: SearchTree = parent 
        self.visit: int = visit      # Number of visits
        self.value: int = value      # Value of node
        self.children: dict[SearchTree] = {}

        self.state: State = state          # Observation
        self.valid_actions: list[str] = None

    def expand(self, valid_actions: list[str]):
        for action in valid_actions:
            if self.player == "main":
                player = "opp"
            else:
                player = "main"

            self.children[action] = SearchTree(player=player, action=action, parent=self)

    def ucb(self, child):
        if child.visit == 0:
            return float('inf')  # Return a very large number to ensure this node gets selected
        else:
            return math.sqrt(math.log(self.visit) / child.visit)

class POMCP():
    """
    Combines Monte-Carlo belief state updates with PO-UCT Algorithm
    """
    def __init__(self,
                 discount=0.8,
                 depth=0,
                 epsilon=1e-7,
                 explore=7,
                 n_particles=128):

        self.discount = discount
        self.depth = depth
        self.epsilon = epsilon
        self.explore = explore
        self.n_particles = n_particles
        self.tree = SearchTree() # This is h
        self.emulator = None
        self.timeout = 1_000_000

    # Search module
    def search(self, state=None):
        # Repeat Simulations until timeout
        for _ in range(self.timeout):
            if state == None:
                # Sample an initial state (observation) and get the initialized pypoker emulator
                state, self.emulator = State.random_state()  # s ~ I(s_0=s)
            self.simulate(state, self.tree, 0)
        return

    def simulate(self, state, tree, depth):
        """
        Simulation performed using the UCT Algorithm
        """
        if tree.state == None:
            tree.state = state
        if tree.valid_actions == None:
            tree.valid_actions = get_valid_actions(state.game_state)
        
        # Keep going down tree until a node with no children is found
        while tree.children:
            # Replace current node with the child that maximized UCB1(s) value
            child = max(tree.children.values(), key=lambda child: child.value + self.explore * tree.ucb(child))
            # Since some children may not have been initialized with state or valid actions
            if child.state == None:
                next_game_state , _ = from_state_action_to_state(tree.state, child.action)
                child.state = State.from_game_state(next_game_state)
            if child.valid_actions == None:
                child.valid_actions = get_valid_actions(child.state.game_state)
            tree = child

        # Now tree is assumed to be a leaf node
        # Check if the node has been traversed
        if tree.visit == 0:
            reward = self.rollout(tree.state, self.emulator)
        else:
            if tree.state == None:
                print("bad")
                exit()
            if tree.valid_actions == None:
                print('bad')
                exit()
                tree.valid_actions = get_valid_actions(tree.state.game_state)
                
            # If node has been visited, expand the tree and perform rollout
            tree.expand(tree.valid_actions)

            # Rollout on first child, other children will eventually get rolled out via UCB1
            action, child_tree = next(iter(tree.children.items()))

            print(f"==>> tree.player: {tree.player}")
            print(f"==>> tree.action: {tree.action}")
            print(f"==>> tree.visit: {tree.visit}")
            print(f"==>> tree.value: {tree.value}")
            print(f"==>> tree.children: {tree.children}")
            print(f"==>> tree.state: {tree.state}")
            print(f"==>> tree.valid_actions: {tree.valid_actions}")
            # Extract resulting state for child node after performing action from parent node
            next_game_state , _ = from_state_action_to_state(tree.state, action)

            tree = child_tree
            tree.state = State.from_game_state(next_game_state)
            tree.valid_acitons = get_valid_actions(next_game_state)

            reward = self.rollout(tree.state, self.emulator)

        # Do backpropogation up the tree
        self.backup(tree, reward)

        return
    
    @staticmethod
    def backup(tree: SearchTree, reward: float):
        """
        Backpropogation step
        Assumption: 0-sum 2-player game
        """
        while tree is not None:
            tree.visit += 1
            # Assign negative reward to Opponent
            # Alternate the reward for 0-sum 2-player poker
            if tree.player == "opp":
                tree.value += reward
            else:
                tree.value -= reward
            
            tree = tree.parent
        
    # NOTE: THIS WORKS
    def rollout(self, state: State, emulator: Emulator):
        cur_stack = state.game_state["table"].seats.players[0].stack
        end_game_state, events = emulator.run_until_round_finish(state.game_state)
        
        reward = end_game_state["table"].seats.players[0].stack - cur_stack
        return reward

def is_round_finish(game_state):
    return game_state["street"] != Const.Street.FINISHED

if __name__ == '__main__':
    from pypokerengine.api.emulator import Emulator
    import pprint
    pp = pprint.PrettyPrinter(indent=2)

    state, emulator = State.random_state()
    # game_state, msg = RoundManager.apply_action(state.game_state, "call")
    pomcp = POMCP()
    pomcp.search()
    pp.pprint(pomcp.rollout(state, emulator))
    
    # num_player = 2
    # max_round = 1000
    # small_blind_amount = 10
    # ante = 0 
    # emulator = Emulator()
    # emulator.set_game_rule(num_player, max_round, small_blind_amount, ante)
    # # emulator.set_game_rule(player_num=3, max_round=10, small_blind_amount=10, ante_amount=0)

    # # 2. Setup GameState object
    # p1_uuid = "uuid-1"
    # p1_model = RandomPlayer(p1_uuid)
    # emulator.register_player(p1_uuid, p1_model)
    # p2_uuid = "uuid-2"
    # p2_model = RandomPlayer(p2_uuid)
    # emulator.register_player(p2_uuid, p2_model)
    # players_info = {
    #     "uuid-1": { "name": "POMCP", "stack": 1000 },
    #     "uuid-2": { "name": "RANDOM", "stack": 1000 },
    # }

    # # print("------------ROUND_STATE(POMCP)--------")
    # # pp.pprint(round_state)
    # # print("------------HOLE_CARD----------")
    # # pp.pprint(hole_card)
    # # print("------------VALID_ACTIONS----------")
    # # pp.pprint(valid_actions)
    # # if len(valid_actions) < 3:
    # #     exit()
    
    # # print("-------------------------------")
    # # game_state = restore_game_state(round_state)
    # # print(game_state)

    # for _ in range(1):
    #     initial_state = emulator.generate_initial_game_state(players_info)
    #     print("------------INITIAL_STATE--------")
    #     pp.pprint(initial_state)
    #     pp.pprint(len(initial_state["table"].seats.players[0].hole_card))
    #     game_state, events = emulator.start_new_round(initial_state)
    #     print("------------GAME_STATE----------")
    #     pp.pprint(game_state)
    #     pp.pprint([str(i) for i in game_state["table"].get_community_card()])
    #     pp.pprint([str(i) for i in game_state["table"].seats.players[0].hole_card])
    #     pp.pprint([str(i) for i in game_state["table"].seats.players[1].hole_card])
    #     print("------------RAISED----------")
    #     game_state, msg = RoundManager.apply_action(game_state, "call")
    #     game_state, msg = RoundManager.apply_action(game_state, "call")
    #     # pp.pprint(game_state)
    #     # pp.pprint(msg)
    #     pp.pprint([str(i) for i in game_state["table"].get_community_card()])
    #     pp.pprint([str(i) for i in game_state["table"].seats.players[0].hole_card])
    #     pp.pprint([str(i) for i in game_state["table"].seats.players[1].hole_card])
    #     print("------------EVENTS----------")
    #     # pp.pprint(events)
    #     end_game_state, events = emulator.run_until_round_finish(game_state)
    #     pp.pprint([end_game_state["table"].seats.players[0].stack])
    #     pp.pprint([str(i) for i in end_game_state["table"].seats.players[0].hole_card])
    #     pp.pprint([str(i) for i in end_game_state["table"].seats.players[1].hole_card])

    #     # RoundManager.apply_action(game_state, )

