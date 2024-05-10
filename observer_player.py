from pypokerengine.players import BasePokerPlayer

# A player that makes its action according to the other player's move
# Assume the other player to be a reasonable player and only raises when chances of winning are big, fold whenver the other player raises

class ObserverPlayer(BasePokerPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        roundNames = [
            "preflop",
            "flop",
            "turn",
            "river",
            "showdown"
        ]
        roundCount = {
           "preflop": 0,
            "flop": 1,
            "turn": 2,
            "river": 3,
            "showdown": 4
        }
        street = round_state['street']
        action_histories = round_state['action_histories']
        # print(round_state)
        # print(street)
        # print(action_histories)

        # Get last action
        last_action = None
        if len(action_histories[street]) < 1:
            last_action = action_histories[roundNames[roundCount[street] - 1]][-1]
        else:
            last_action = action_histories[street][-1]
        # Call if the other player called
        if last_action['action'] == 'CALL':
            return "call"
        elif last_action == 'RAISE':
            return "fold"
        return "call"

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
  return ObserverPlayer()