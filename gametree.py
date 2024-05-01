import itertools
import random
# import pypokerengine.handprobability as handprobability
import handprobability

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
                 dist=None):
        
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

        # Defines if node is a leaf
        self.is_terminal = self.is_terminal_history()

        self.dist = dist

        # value determines how 'good' a node is
        if self.is_terminal_history():
            self.value = self.evaluation()
        else:
            # None if it is not a leaf node on instantiation
            self.value = None

        # See tree
        # print(self.pot, self.value, self.history, self.hole_cards, self.community_cards)

    def add_child(self, child):
        self.children.append(child)

    # TODO: Set calculation time/iter limits
    def evaluation(self):
        # h_1(x) (expected value of pot)
        pot = self.pot
        full_result_dict = self.dist
        win_loss = full_result_dict['WinLossTie']
        print(win_loss)
        if self.action == 'call':
            value = (win_loss[0])
        if self.action == 'fold':
            value = (win_loss[1])

        # h_2(x)
        # ...

        return value
    
    # Determines if a history array has terminated
    def is_terminal_history(self):
        # Call is terminal if it is not the first move made. Fold always terminates. Raise never terminates
        if (len(self.history) > 1 and self.history[-1] == 'call') or (len(self.history) and self.history[-1] == 'fold'):
            return True
        return False
    
    # Returns true if the node represents the small blind limping
    def is_special_call_node(self):
        if (len(self.history) == 1 and self.history[0] == 'call'):
            return True
        return False
    
    def to_string(self):
        print(self.history, self.action, self.value)

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
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.history = history
        self.current_pot = pot

        # Determine starting player based on the given history
        # small blind plays every even turn
        self.starting_player = 'small_blind' if len(self.history) % 2 == 0 else 'big_blind'

        # Get raise count in history
        self.raise_count = sum([1 for r in history if r == 'raise'])

        self.hand_dist = handprobability.getWinLossTieOdds(self.hole_cards, self.community_cards, 100, 3000)

    def build_tree(self):
        # Do not calculate a tree if the last move was a fold
        # Should never occur: edge case
        # if self.is_terminal_history(self.history):
        #     return self.root

        # Create a root node from the known current game state
        self.root = BettingNode(player=self.starting_player,
                                pot=self.current_pot,
                                hole_cards=self.hole_cards,
                                community_cards=self.community_cards,
                                raise_count=self.raise_count,
                                history=self.history,
                                dist=self.hand_dist)

        # Generate a tree
        if not self.root.is_terminal:
            self.generate_children(self.root)

        # self.recursive_children_count(self.root)

        return self.root
    
    # Recursively generate a sub-tree tree from a given node
    def generate_children(self, parent_node:BettingNode):
        # Do nothing if terminal
        if parent_node.is_terminal:
            return
        
        if parent_node.player == 'small_blind':
            next_player = 'big_blind'
        else:
            next_player = 'small_blind'

        # Checks if a raise is allowed
        does_raise = parent_node.raise_count < LimitPokerTree.MAX_RAISES

        # --------------- Fold ---------------

        # Terminate on a fold - do not generate new child game states
        fold_node = BettingNode(player=next_player,
                                action='fold',
                                pot=parent_node.pot,
                                parent=parent_node,
                                raise_count=parent_node.raise_count,
                                hole_cards=self.hole_cards,
                                community_cards=self.community_cards,
                                history=[*parent_node.history, 'fold'],
                                dist=self.hand_dist)

        parent_node.add_child(fold_node)

        # --------------- Call ---------------

        # Add the correct amount to the pot based on the action
        pot_after_action = parent_node.pot

        # Only add 10 if the big blind does not call after the small blind limps
        if not parent_node.is_special_call_node():
            pot_after_action += self.SMALL_BLIND

        action_node = BettingNode(player=next_player,
                                    action='call',
                                    pot=pot_after_action,
                                    parent=parent_node,
                                    raise_count=parent_node.raise_count,
                                    hole_cards=self.hole_cards,
                                    community_cards=self.community_cards,
                                    history=[*parent_node.history, 'call'],
                                    dist=self.hand_dist)

        parent_node.add_child(action_node)
        
        # Betting only continues on raise or if small blind limps
        if not action_node.is_terminal:
            self.generate_children(action_node)

        # --------------- Raise ---------------

        if does_raise:
            # Only add 10 if the big blind is raising after a limp
            if parent_node.is_special_call_node():
                pot_after_action += self.SMALL_BLIND

            # Add 20 if they raise (see + 10, raise + 10)
            else:
                pot_after_action += self.BIG_BLIND

            # Create a node for the selected action
            action_node = BettingNode(player=next_player,
                                        action='raise',
                                        pot=pot_after_action,
                                        parent=parent_node,
                                        raise_count=parent_node.raise_count + 1,
                                        hole_cards=self.hole_cards,
                                        community_cards=self.community_cards,
                                        history=[*parent_node.history, 'raise'],
                                        dist=self.hand_dist)

            parent_node.add_child(action_node)

            # Betting only continues on raise or if small blind limps
            if not action_node.is_terminal:
                self.generate_children(action_node)

        value_sum = sum(map(lambda node: node.value, parent_node.children))
        if does_raise:
            parent_node.value = value_sum / 3
        else:
            parent_node.value = value_sum / 2
    
    # Calculate the number of nodes in the tree
    def recursive_children_count(self, node:BettingNode):
        if not node:
            return 0
        node.to_string()
        return sum(map(self.recursive_children_count, node.children)) + 1

    def getNodeAction(self):
        children = self.root.children
        odds = [child.value for child in children]
        total = sum(odds)
        if total == 0:
            return 'call'
        odds = [x/total for x in odds]
        #print(odds)
        cumulativeOdds = []
        lenOdds = len(odds)
        for i in range(lenOdds):
            cumulativeOdds.append(sum(odds[0:i+1]))
        sample = random.uniform(0,1)
        i = 0
        while not i > lenOdds - 1 and sample >= cumulativeOdds[i]:
            i += 1
        if i == 0:
            #print('fold')
            return 'fold'
        if i == 1:
            #print('call')
            return 'call'
        if i == 2:
            #print('raise')
            return 'raise'

        



if __name__ == '__main__':
    tree = LimitPokerTree(["C6", "DK"], [], [], 30)
    tree.build_tree()
    tree.getNodeAction()