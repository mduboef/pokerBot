import random

#TODO: Think about ways to make this smarter like configuring the random distributions away from random uniform across all potential values (e.g., skewed gaussian)

class Observation:
    def __init__(self, hole_card: list[str], round_state: dict) -> None:
        self.hole_card = hole_card
        self.community_card = round_state['community_card']
        self.round_state = round_state

    def _gen_op_hole_cards(self):
        hole_card = self.hole_card
        community_card = self.community_card
        # Define suits, ranks, and generate the full deck of cards
        suits = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [f"{suit}{rank}" for rank in ranks for suit in suits]

        # Remove known cards from deck (hole cards of player 1 and visible community cards)
        known_cards = hole_card + [card for card in community_card]
        remaining_deck = [card for card in deck if card not in known_cards]

        # Generate possible hole cards for player 2 from the remaining deck
        return random.sample(remaining_deck, 2)
    
    def sample_state(self):
        """
        Samples random state given observation
        """
        return State(self.hole_card, self._gen_op_hole_cards(), self.round_state)
    
class State:
    def __init__(self, hole_card_main: list[str], hole_card_op: list[str], round_state: dict) -> None:
        self.hole_card_main = hole_card_main
        self.hole_card_op = hole_card_op
        self.community_card = round_state['community_card']
        self.round_state = round_state
    
    def get_observation(self):
        return Observation(self.hole_card_main, self.round_state)
    
    @classmethod
    def from_game_state(cls, game_state: dict, hole_card_main: list[str], hole_card_op: list[str]):
        return cls(hole_card_main, hole_card_op, game_state['round_state']['community_card'], game_state['round_state'])

def get_current_player_id(round_state):
    return round_state['next_player']

def calculate_valid_actions(round_state, player_id):
    current_player = round_state['seats'][player_id]
    current_stack = current_player['stack']
    current_call_amount = round_state['call_amount']
    min_raise, max_raise = round_state['min_raise'], round_state['max_raise']

    actions = []
    actions.append({'action': 'fold'})

    if current_call_amount > 0:
        if current_stack >= current_call_amount:
            actions.append({'action': 'call'})
        if current_stack >= min_raise:
            actions.append({'action': 'raise'})

    return actions

# Function to generate a random game state given current observation
def generate_random_game_state(round_state, hole_card: list) -> str:
    """
        Outputs the same format from generate_random_game_observation() and generate_random_game_state()
    Input is of the format:
    { 'action_histories': { 'flop': [ { 'action': 'RAISE',
                                    'add_amount': 40,
                                    'amount': 40,
                                    'paid': 40,
                                    'uuid': 'bzggcmuaoypqacyvhaigyh'},
                                  { 'action': 'RAISE',
                                    'add_amount': 40,
                                    'amount': 80,
                                    'paid': 80,
                                    'uuid': 'viqojmltetkdspzyvgljuy'},
                                  { 'action': 'CALL',
                                    'amount': 80,
                                    'paid': 40,
                                    'uuid': 'bzggcmuaoypqacyvhaigyh'}],
                        'preflop': [ { 'action': 'SMALLBLIND',
                                       'add_amount': 20,
                                       'amount': 20,
                                       'uuid': 'bzggcmuaoypqacyvhaigyh'},
                                     { 'action': 'BIGBLIND',
                                       'add_amount': 20,
                                       'amount': 40,
                                       'uuid': 'viqojmltetkdspzyvgljuy'},
                                     { 'action': 'RAISE',
                                       'add_amount': 40,
                                       'amount': 80,
                                       'paid': 60,
                                       'uuid': 'bzggcmuaoypqacyvhaigyh'},
                                     { 'action': 'CALL',
                                       'amount': 80,
                                       'paid': 40,
                                       'uuid': 'viqojmltetkdspzyvgljuy'}],
                        'river': [],
                        'turn': [ { 'action': 'CALL',
                                    'amount': 0,
                                    'paid': 0,
                                    'uuid': 'bzggcmuaoypqacyvhaigyh'},
                                  { 'action': 'CALL',
                                    'amount': 0,
                                    'paid': 0,
                                    'uuid': 'viqojmltetkdspzyvgljuy'}]},
    'big_blind_pos': 1,
    'community_card': ['C7', 'CQ', 'HT', 'CT', 'CJ'],
    'dealer_btn': 1,
    'next_player': 0,
    'pot': {'main': {'amount': 320}, 'side': []},
    'round_count': 110,
    'seats': [ { 'name': 'Your agent',
                'stack': 12620,
                'state': 'participating',
                'uuid': 'bzggcmuaoypqacyvhaigyh'},
                { 'name': 'Your agent',
                'stack': 7060,
                'state': 'participating',
                'uuid': 'viqojmltetkdspzyvgljuy'}],
    'small_blind_amount': 20,
    'small_blind_pos': 0,
    'street': 'river'}
    """
    
    # Define suits, ranks, and generate the full deck of cards
    suits = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [f"{suit}{rank}" for rank in ranks for suit in suits]

    # Extract community cards and ensure there are always 5 cards, filled with "00" if fewer
    community_cards = round_state['community_card'] + ['00'] * (5 - len(round_state['community_card']))

    # Remove known cards from deck (hole cards of player 1 and visible community cards)
    known_cards = hole_card + [card for card in round_state['community_card'] if card != '00']
    remaining_deck = [card for card in deck if card not in known_cards]

    # Extract the pot amount from the main pot
    pot = round_state['pot']['main']['amount']
    # Extract the current round count
    rounds = round_state['round_count']
    player1_cards = hole_card
    # Generate possible hole cards for player 2 from the remaining deck
    player2_cards = random.sample(remaining_deck, 2)

    # Combine all parts into the final encoded string
    game_state = f"{''.join(community_cards)}|{str(pot).zfill(5)}|{str(rounds).zfill(5)}|{''.join(player1_cards)}|{''.join(player2_cards)}"
    return game_state

def to_game_observation(round_state: dict, hole_card: list) -> str:
    # Extract community cards and ensure there are always 5 cards, filled with "00" if fewer
    community_cards = round_state['community_card'] + ['00'] * (5 - len(round_state['community_card']))
    
    # Extract the pot amount from the main pot
    pot = round_state['pot']['main']['amount']
    
    # Extract the current round count
    rounds = round_state['round_count']
    
    player1_cards = hole_card
    player2_cards = ['00', '00']  # Placeholder since actual cards are unknown
    
    # Combine all parts into the final encoded string
    game_state = f"{''.join(community_cards)}|{str(pot).zfill(5)}|{str(rounds).zfill(5)}|{''.join(player1_cards)}|{''.join(player2_cards)}"
    return game_state

# def eval_hole_cards(hole_card):
#     score = 0
#     card_1, card_2 = hole_card[0], hole_card[1]
#     is_same_suit = card_1[0] == card_2[0]
#     is_pair = card_1[1] == card_2[1]
#     is_ace = card_1[1] == 'A' or card_2[1] == 'A'

#     is_high_pair = is_pair and (card_1[1] == 'A' or card_1[1] == 'K' or card_1[1] == 'Q')
#     is_mid_pair = is_pair and (card_1[1] == 'J' or card_1[1] == 'T')
#     if is_high_pair:
#         score += 10
#     elif is_mid_pair:
#         score += 9
#     elif is_pair:
#         score += 8
    


if __name__ == "__main__":
    print(generate_random_game_state())