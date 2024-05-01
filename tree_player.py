from pypokerengine.players import BasePokerPlayer
import pypokerengine.gametree as gt

class TreePlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    parsed_history = []
    action_histories = round_state['action_histories']
    rounds = list(action_histories.keys())
    curr_round = action_histories[rounds[-1]]
    parsed_history = [x['action'].lower() for x in curr_round if x['action'] == 'RAISE' or x['action'] == 'CALL' or x['action'] == 'FOLD']
    pot = round_state['pot']['main']['amount'] + sum(map(lambda x: x['amount'], round_state['pot']['side']))
    tree = gt.LimitPokerTree(hole_cards=hole_card, community_cards=round_state['community_card'], history=parsed_history, pot=pot)
    tree.build_tree()
    action_choice = tree.getNodeAction()
    return action_choice

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
  return TreePlayer()
