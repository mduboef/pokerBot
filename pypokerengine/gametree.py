import itertools
import random
import sys
import timeit

class BettingNode:
    def __init__(self,
                 player,
                 action=None,
                 raise_count=0,
                 pot=0,
                 hole_cards=None,
                 community_cards=None,
                 history=[],
                 parent=None, 
                 value=0):
        
        # Player deciding which move to make next
        self.player = player

        # Action that was used to get to this node
        self.action = action

        # number of raises made up to this point
        self.raise_count = raise_count

        # Amount of money in the pot
        self.pot = pot

        # Cards in your hand
        self.hole_cards = hole_cards

        # Cards on the table known to everyone
        self.community_cards = community_cards

        # Parent node
        self.parent = parent

        # Game states following this one
        self.children = []

        # Full history used to get to this point
        self.history = history

        # value determines how 'good' a node is
        self.value = value

        print(self.pot, self.value, self.history)

    def add_child(self, child):
        self.children.append(child)

class LimitPokerTree:
    SMALL_BLIND = 10
    BIG_BLIND = 20
    MAX_RAISES = 4

    """
    Tree for a single round of betting:

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

    Values of nodes should be probabilities based on assumed opponent policy vs child values
    """

    # Demo history format:
    # history = ['call', 'raise', 'raise', ...]
    def __init__(self, hole_cards, community_cards, history, pot):
        self.root = None

        # Given game state data
        self.my_hole_cards = hole_cards
        self.community_cards = community_cards
        self.history = history
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
        self.root = BettingNode(player=self.starting_player,
                                pot=self.current_pot,
                                hole_cards=self.my_hole_cards,
                                community_cards=self.community_cards,
                                raise_count=self.raise_count,
                                history=self.history,
                                value=self.current_pot)

        # Generate a tree
        if not self.is_terminal_history(self.root.history):
            self.generate_children(self.root)
    
        return self.root
    
    # Recursively generate a sub-tree tree from a given node
    def generate_children(self, parent_node):

        # Generate possible actions for a player: fold, call, raise (if raises are left)
        actions = ['fold', 'call']
        if parent_node.raise_count < self.MAX_RAISES:
            actions.append('raise')

        for action in actions:
            # Add to the history of the new node
            new_history = [*parent_node.history, action]
            if action == 'fold':
                # Terminate on a fold - do not generate new child game states
                fold_node = BettingNode(player=self.next_player(parent_node.player),
                                        action='fold',
                                        pot=parent_node.pot,
                                        parent=parent_node,
                                        raise_count=parent_node.raise_count,
                                        history=new_history,
                                        value=parent_node.pot)
                
                parent_node.add_child(fold_node)

            # Add the correct amount to the pot based on the action
            else:
                pot_after_action = parent_node.pot

                # Only add 10 if the big blind does not call after the small blind limps
                if action == 'call' and not self.is_special_call_node(parent_node.history):
                    pot_after_action += self.SMALL_BLIND

                # Only add 10 if the big blind is raising after a limp
                elif action == 'raise' and self.is_special_call_node(parent_node.history):
                    pot_after_action += self.SMALL_BLIND

                # Add 20 if they raise (see + 10, raise + 10)
                elif action == 'raise':
                    pot_after_action += self.BIG_BLIND

                # Create a node for the selected action
                action_node = BettingNode(player=self.next_player(parent_node.player),
                                          action=action,
                                          pot=pot_after_action,
                                          parent=parent_node,
                                          raise_count=parent_node.raise_count + (1 if action == 'raise' else 0),
                                          history=new_history,
                                          value=pot_after_action)
                
                parent_node.add_child(action_node)

                # Betting only continues on raise or if small blind limps
                if not self.is_terminal_history(action_node.history):
                    self.generate_children(action_node)

    # Calculates the next player
    def next_player(self, player):
        if player == 'small_blind':
            return 'big_blind'
        return 'small_blind'
    
    # Determines if a history array has terminated
    def is_terminal_history(self, history):
        # Call is terminal if it is not the first move made. Fold always terminates
        if (len(history) > 1 and history[-1] == 'call') or (len(history) and history[-1] == 'fold'):
            return True
        return False
    
    # Returns true if the node represents the small blind limping
    def is_special_call_node(self, history):
        if (len(history) == 1 and history[0] == 'call'):
            return True
        return False
    
    # Calculate the number of nodes in the tree
    def recursive_children_count(self, node):
        if not node:
            return 0
        return sum(map(self.recursive_children_count, node.children)) + 1

# Test tree generation
tree = LimitPokerTree(['AH', 'JC'], [], [], 30)
tree.build_tree()
print(tree.recursive_children_count(tree.root))