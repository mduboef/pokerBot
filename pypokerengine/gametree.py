import itertools
import random
import sys

class BettingNode:
    def __init__(self, player, action=None, raise_count=0, pot=0, hole_cards=None, community_cards=None, history=[], parent=None):
        self.player = player
        self.action = action
        self.raise_count = raise_count
        self.pot = pot
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.parent = parent
        self.children = []
        self.history = history

        print(self.history)

    def add_child(self, child):
        self.children.append(child)

class LimitPokerTree:
    SMALL_BLIND = 10
    BIG_BLIND = 20
    MAX_RAISES = 4

    """
    Tree:

    .
    └── S/
        ├── F
        ├── C/ --- The edge case node causing problems (only call that continues the game tree)
        │   ├── F
        │   ├── C -- Edge case where no money is added to the pot
        │   └── R/
        │       ├── F
        │       ├── C
        │       └── R/
        │           ├── F
        │           ├── C
        │           └── R/
        │               ├── F
        │               ├── C
        │               └── R/
        │                   ├── F
        │                   └── C
        └── R/
            ├── F
            ├── C
            └── R/
                ├── F
                ├── C
                └── R/
                    ├── F
                    ├── C
                    └── R/
                        ├── F
                        └── C

    Anomaly node occurs when the small blind calls and the big blind has not made a move.
    The big blind calls after it, and adds no money to the pot, also causing an edge case
    """

    # Demo history format:
    # history = ['call', 'raise', 'raise', ...]
    def __init__(self, hole_cards, community_cards, history, pot):
        self.root = None

        # Given game state data
        self.my_hole_cards = hole_cards
        self.community_cards = community_cards
        self.history = history

        # Take history into account to get the pot: raise + 20, call + 10, fold +0
        self.current_pot = pot

        # Determine starting player based on the given history
        # small blind plays every even turn
        self.starting_player = 'small_blind' if len(self.history) % 2 == 0 else 'big_blind'

        # Get raise count in history
        self.raise_count = sum([1 for r in history if r == 'raise'])

    def build_tree(self):
        # Do not calculate a tree if the last move was a fold
        # Should never occur: edge case
        if self.is_terminal_history(self.history):
            return self.root

        # Create a root node from the known current game state
        self.root = BettingNode(player=self.starting_player, pot=self.current_pot, hole_cards=self.my_hole_cards, community_cards=self.community_cards, raise_count=self.raise_count, history=self.history)

        # Generate a tree
        if not self.is_terminal(self.root):
            self.generate_children(self.root)
    
        return self.root
    
    # TODO: Check terminal with node history
    def generate_children(self, parent_node):

        # Generate possible actions for a player: fold, call, raise (if raises are left)
        actions = ['fold', 'call']
        if parent_node.raise_count <= self.MAX_RAISES:
            actions.append('raise')

        for action in actions:
            new_history = [*parent_node.history, action]
            if action == 'fold':
                # Add a fold node and no further children
                fold_node = BettingNode(player=self.next_player(parent_node.player), action='fold', pot=parent_node.pot, parent=parent_node, raise_count=parent_node.raise_count, history=new_history)
                parent_node.add_child(fold_node)
            else:
                pot_after_action = parent_node.pot
                if action == 'call':
                    pot_after_action += self.BIG_BLIND
                elif action == 'raise':
                    pot_after_action += self.BIG_BLIND  # Assuming a fixed raise amount

                # Create a node for the action
                action_node = BettingNode(player=self.next_player(parent_node.player), action=action, pot=pot_after_action, parent=parent_node, raise_count=parent_node.raise_count + (1 if action == 'raise' else 0), history=new_history)
                parent_node.add_child(action_node)

                # Betting only continues on raise or if small blind calls as the first move
                if not self.is_terminal(action_node):
                    self.generate_children(action_node)

    # Calculates the next player
    def next_player(self, player):
        if player == 'small_blind':
            return 'big_blind'
        return 'small_blind'

    # Determine if the node is a terminal node
    def is_terminal(self, node):
        # The only call that does not terminate is the small blind calling before big blind gets a turn
        return self.is_terminal_history(node.history)
    
    # Determines if a history array has terminated
    def is_terminal_history(self, history):
        if (len(history) == 2 and history[0] == 'call' and history[1] == 'call') or (len(history) and history[-1] == 'fold') or(history[-1] == 'call'):
            return True
        return False
    
    # Calculate the number of nodes in the tree
    def recursive_children_count(self, node):
        if not node:
            return 0
        # print(node.raise_count, self.next_player(node.player), node.action)
        return sum(map(self.recursive_children_count, node.children)) + 1


tree = LimitPokerTree(['AH', 'JC'], [], ['raise'], 0)
tree.build_tree()
print(tree.starting_player, tree.current_pot)
print(tree.recursive_children_count(tree.root))

sys.exit(0)