import random

#TODO: Think about ways to make this smarter like configuring the random distributions away from random uniform across all potential values (e.g., skewed gaussian)

# Define suits, ranks, and generate the full deck of cards
suits = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
deck = [f"{suit}{rank}" for rank in ranks for suit in suits]

# Define maximum pot and rounds (as string for easy formatting)
max_pot = 99999 # TODO: probably less
max_rounds = 99999 # TODO: probably less

# Function to randomly select exactly two cards for each player
def get_two_cards():
    selected_cards = random.sample(deck, 2)
    return selected_cards

# Function to generate a random game state
def generate_random_game_state() -> str:
    # Randomly select the number of community cards between 2 and 5
    num_community_cards = random.randint(2, 5)
    community_cards = random.sample(deck, num_community_cards)
    # Fill the remaining card slots with "00" up to 5 cards
    community_cards += ['00'] * (5 - num_community_cards)
    
    remaining_deck = list(set(deck) - set(community_cards))

    # Randomly select two hole cards for each player from the remaining deck
    player1_cards = random.sample(remaining_deck, 2)
    remaining_deck = list(set(remaining_deck) - set(player1_cards))
    player2_cards = random.sample(remaining_deck, 2)

    # Randomly select pot and round numbers, and format them
    pot = random.randint(1, max_pot)
    rounds = random.randint(1, max_rounds)

    # Combine all parts into the final encoded string
    game_state = f"{''.join(community_cards)}|{str(pot).zfill(5)}|{str(rounds).zfill(5)}|{''.join(player1_cards)}|{''.join(player2_cards)}"
    return game_state


def generate_random_game_observation() -> str:
    # Randomly select the number of community cards between 2 and 5
    num_community_cards = random.randint(2, 5)
    community_cards = random.sample(deck, num_community_cards)
    # Fill the remaining card slots with "00" up to 5 cards
    community_cards += ['00'] * (5 - num_community_cards)
    
    remaining_deck = list(set(deck) - set(community_cards))

    # Randomly select two hole cards for each player from the remaining deck
    player1_cards = random.sample(remaining_deck, 2)
    remaining_deck = list(set(remaining_deck) - set(player1_cards))
    player2_cards = random.sample(remaining_deck, 2)

    # Randomly select pot and round numbers, and format them
    pot = random.randint(1, max_pot)
    rounds = random.randint(1, max_rounds)

    # Combine all parts into the final encoded string
    game_state = f"{''.join(community_cards)}|{str(pot).zfill(5)}|{str(rounds).zfill(5)}|{''.join(player1_cards)}|{''.join("0000")}"
    return game_state

def game_state_to_str(round_state: dict, hole_card_player_1: list, hole_card_player_2: list) -> str:
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
    community_cards = round_state['community_card'].join("")
    pot = str(round_state['pot']['main']['amount']).zfill(5)
    rounds = str(round_state['round_count']).zfill(5)
    hole_card_player_1 = hole_card_player_1.join("")
    hole_card_player_2 = hole_card_player_2.join("")
    game_state = f"{''.join(community_cards)}|{str(pot).zfill(5)}|{str(rounds).zfill(5)}|{''.join(hole_card_player_1)}|{''.join(hole_card_player_2)}"
    
    return game_state

if __name__ == "__main__":
    print(generate_random_game_observation())