import random
from pypokerengine.api.emulator import Emulator
from pypokerengine.engine.card import Card
from pypokerengine.engine.deck import Deck
from pypokerengine.engine.message_builder import MessageBuilder
from pypokerengine.utils.card_utils import gen_deck, gen_cards
from randomplayer import RandomPlayer
from pypokerengine.engine.round_manager import RoundManager

#TODO: Think about ways to make this smarter like configuring the random distributions away from random uniform across all potential values (e.g., skewed gaussian)

class State:
    def __init__(self, hole_card_main: list[str], community_cards: list[str], game_state: dict) -> None:
        self.hole_card_main = hole_card_main
        self.community_card = community_cards
        # self.opp_previous_action = ... # TODO Implement
        self.state_info = self.get_state_info_str(hole_card_main, community_cards)
        self.game_state = game_state
    
    @classmethod
    def from_game_state(self, game_state: dict):
        self.hole_cards_main = [str(i) for i in game_state["table"].seats.players[0].hole_card]
        # opp_hole = [str(i) for i in game_state["table"].seats.players[1].hole_card]
        # print(f"==>> opp_hole: {opp_hole}")
        # print(f"==>> self.hole_cards_main: {self.hole_cards_main}")
        self.community_cards = [str(i) for i in game_state["table"].get_community_card()]
        self.state_info = self.get_state_info_str(self.hole_cards_main, self.community_cards)
        self.game_state = game_state
        return self

    @staticmethod
    def get_state_info_str(hole_cards, community_cards):
        return f"{''.join(community_cards)}|{''.join(hole_cards)}"
    
    @classmethod
    def random_state(self):
        """
        Generates a random state of the game.
        Since we can't initialize a game state along with the player's hoe cards, we do a hacky version
        """
        num_player = 2
        max_round = 10000000000
        small_blind_amount = 10
        ante = 0 
        emulator = Emulator()
        emulator.set_game_rule(num_player, max_round, small_blind_amount, ante)

        # 2. Setup GameState object
        p1_uuid = "uuid-1"
        p1_model = RandomPlayer(p1_uuid)
        emulator.register_player(p1_uuid, p1_model)
        p2_uuid = "uuid-2"
        p2_model = RandomPlayer(p2_uuid)
        emulator.register_player(p2_uuid, p2_model)
        players_info = {
            "uuid-1": { "name": "POMCP", "stack": 1000 },
            "uuid-2": { "name": "RANDOM", "stack": 1000 },
        }

        # Initializes the initial game state without dealing
        initial_state = emulator.generate_initial_game_state(players_info)
        # Actually starts the round and is now a player's turn
        # Hoe cards have been distributed, but not community cards
        game_state, events = emulator.start_new_round(initial_state)

        hole_cards_main = [str(i) for i in game_state["table"].seats.players[0].hole_card]

        # Create instance first then use it to call get_state_info_str
        self.hole_cards = hole_cards_main
        # print(f"==>> self.hole_cards: {self.hole_cards}")

        self.community_cards = []
        self.state_info = self.get_state_info_str(self.hole_cards, [])
        self.game_state = game_state

        # Community cards is empty
        return self, emulator

    def matches(self, hole_card_main=None, community_cards=None):
        if hole_card_main is not None and self.hole_card_main != hole_card_main:
            return False
        if community_cards is not None and self.community_card != community_cards:
            return False
        return True

def get_current_player_id(round_state):
    return round_state['next_player']

def get_valid_actions(game_state: dict) -> list[dict]:
    # Extracted from run_until_round_finish()
    next_player_pos = game_state["next_player"]
    msg = MessageBuilder.build_ask_message(next_player_pos, game_state)["message"]
    extracted_valid_actions = extract_valid_actions(msg["valid_actions"])
    assert extract_valid_actions != None, "valid actions should not be none"
    return extracted_valid_actions
 
def extract_valid_actions(valid_actions: list[dict]) -> list[str]:
    """
    Pypoker engine has actions: {'action': 'call'}
    This function extracts the action strings
    """
    extracted_actions = [action_dict['action'] for action_dict in valid_actions]
    return extracted_actions

def from_state_action_to_state(emulator: Emulator, game_state: dict, action: str):
    # TODO: check if emulator or RoundManger is correct since they both have apply_action()
    # MCTS works with RoundManager
    new_game_s, messages = emulator.apply_action(game_state, action)
    return new_game_s, messages

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
    


if __name__ == "__main__":
    print(generate_random_game_state())