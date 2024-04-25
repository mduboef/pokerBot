
# The agent’s action,
# denoted by a, is determined by the current round state. Each state of the game
# consists of four components:
# 1. The private cards visible to the player.
# 2. The community cards visible to both player and opponent.
# 3. The current bet placed by you and
# 4. The current bet placed by the opponent.
# 5. This one is not listed in the instruction but also should be considered: how much money the opponent have (sum to 20000)

# Simple implementation using Monte Carlo Sampling
# Argument: the opponent will determine its next move based on the 5 states and
# They may also make their action based on the history, which is basically taking our player's action into consideration
# To take this part into account we would be basically predicting how the opponent predicts our action, which is nested
# We can probably ignore the history for now.

GUESS_PROB = 1/3
# Each state maintains a set of probabilities of transitioning to other states
class State:
    def __init__(self, hole_cards, community_cards, betted, opponent_bet, pocket_level): # pocket refers to how much money the opponent has
        # The instruction seems to have conflicting use of pot
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.betted = betted # Not implemented in game tree
        self.opponent_bet = opponent_bet # Not implemented in game tree
        self.pocket = pocket_level # 6 intervals
        self.transition_dict = {}
        self.seen_times = 0

    # Given a current state and an action, the next state is deterministic
    def record_move(self, action):
        self.seen_times += 1
        if action not in self.prob_dict:
            self.transition_dict[(action)] = 1
        else:
            self.transition_dict[(action)] += 1

    # Calculate the next state using an action
    # I don't think this part is neccessary, the game tree will to the calculation
    def __calc_next_state(cur_state, action): 
        return 0
    
    def get_probability(self, action):
        # Should think about what the initial value is
        if self.seen_times == 0:
            return GUESS_PROB
        if (action) not in self.prob_dict:
            return 0
        else:
            return self.transition_dict[action] / self.seen_times

# Does not keep track of all the information, only the odd/ even levels
class OpponentAction:
    # Divide the total money in 6 intervals
    # interval 1
    LOSING = 3334
    # interval 2
    LOW = 6667
    # interval 3
    EVEN = 10000
    # interval 4
    HIGH = 13334
    # interval 5
    WINNING = 16667
    # interval 6
    def __init__(self):
        self.last_action = None
        self.states = {} # Could integrate State into OpponentAction to use less memory, though this provides modularity
        # states = {
        #     "(hole_cards, community_cards, betted, pocket_level)": State
        # }
    
    def __calc_pocket_level(self, pocket):
        pocket_level = 0
        if pocket < self.LOSING:
            pocket_level = 1
        elif pocket < self.LOW:
            pocket_level = 2
        elif pocket < self.EVEN:
            pocket_level = 3
        elif pocket < self.HIGH:
            pocket_level = 4
        elif pocket < self.WINNING:
            pocket_level = 5
        elif pocket >= self.WINNING:
            pocket_level = 6
        else: print('invalid pocket')
        return pocket_level

    
    # Gametree should call this function when the opponent makes a move
    def update(self, action, hole_cards, community_cards, betted, opponent_bet, pocket):
        pocket_level = self.__calc_pocket_level(pocket)
        cur_state = None
        # Create a new State if first seen, else update old object
        if ((hole_cards, community_cards, betted, pocket_level)) not in self.states:
            cur_state = State(hole_cards, community_cards, betted, opponent_bet, pocket_level)
        else:
            cur_state = self.states[(hole_cards, community_cards, betted, pocket_level)]
        # record last move
        if self.last_action is not None:
            self.last_action.record_move(action)
        self.last_action = cur_state
    

    def predict(self, hole_cards, community_cards, betted, pocket, action):
        pocket_level = self.__calc_pocket_level(pocket)
        if ((hole_cards, community_cards, betted, pocket_level)) not in self.states:
            return GUESS_PROB
        else:
            cur_state = self.states[(hole_cards, community_cards, betted, pocket_level)]
            return cur_state.get_probability(action)
    
# How to use: initiate an OpponentAction object at the start of the game, 
# call OpponentAction.update every time the opponent makes a move
# call predict when needing to know the probability of the next move