import itertools
import random
import pypokerengine.handprobability as handprobability

class BettingNode:
    def __init__(self,
                 player,
                 action=None,
                 raise_count=0,
                 pot=0,
                 hole_cards=None,
                 community_cards=None,
                 history=[],
                 parent=None):
        
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
        full_result_dict = handprobability.getWinLossTieOdds(self.hole_cards, self.community_cards, 50, 3000)
        win_loss = full_result_dict['WinLossTie']
        if self.action == 'call':
            value = (win_loss[0])*pot
        if self.action == 'fold':
            value = (win_loss[1])*pot

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
        # if self.is_terminal_history(self.history):
        #     return self.root

        # Create a root node from the known current game state
        self.root = BettingNode(player=self.starting_player,
                                pot=self.current_pot,
                                hole_cards=self.my_hole_cards,
                                community_cards=self.community_cards,
                                raise_count=self.raise_count,
                                history=self.history)

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
                                        hole_cards=self.my_hole_cards,
                                        community_cards=self.community_cards,
                                        history=new_history)

                parent_node.add_child(fold_node)

            # Add the correct amount to the pot based on the action
            else:
                pot_after_action = parent_node.pot

                # Only add 10 if the big blind does not call after the small blind limps
                if action == 'call' and not parent_node.is_special_call_node():
                    pot_after_action += self.SMALL_BLIND

                # Only add 10 if the big blind is raising after a limp
                elif action == 'raise' and parent_node.is_special_call_node():
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
                                          hole_cards=self.my_hole_cards,
                                          community_cards=self.community_cards,
                                          history=new_history)

                parent_node.add_child(action_node)

                # Betting only continues on raise or if small blind limps
                if not action_node.is_terminal:
                    self.generate_children(action_node)

        if len(parent_node.children) > 0:
            value_sum = sum(map(lambda node: node.value, parent_node.children))
            value_avg = value_sum / len(parent_node.children)
        else:
            value_avg = None
        
        parent_node.value = value_avg

    # Calculates the next player
    def next_player(self, player):
        if player == 'small_blind':
            return 'big_blind'
        return 'small_blind'
    
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
        odds = [x/total for x in odds]
        cumulativeOdds = []
        for i in range(len(odds)):
            cumulativeOdds.append(sum(odds[0:i+1]))
        sample = random.uniform(0,1)
        i = 0
        while not i > len(odds) - 1 and sample >= cumulativeOdds[i]:
            i += 1
        # print(sample)
        # print(cumulativeOdds)
        if i == 0:
            # print('fold')
            return 'fold'
        if i == 1:
            # print('call')
            return 'call'
        if i == 2:
            # print('raise')
            return 'raise'

        



if __name__ == '__main__':
    tree = LimitPokerTree(["C6", "DK"], [], [], 30)
    tree.build_tree()
    tree.getNodeAction()