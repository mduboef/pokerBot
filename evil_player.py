from pypokerengine.players import BasePokerPlayer
import gametree as gt
import handprobability as handProb
import timeit
import random as rand

#IDEA: Rip off angela's agent and see if it works.

class EvilPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    if hole_card[0][0] == hole_card[1][0]:
      sample = rand.uniform(0,1)
      if sample <= .5:
        return 'call'
      return 'raise'
    if hole_card[0][1] == hole_card[1][1]:
      sample = rand.uniform(0,1)
      if sample <= .5:
        return 'call'
      return 'raise'
    if hole_card[0][1] in ['T', 'J', 'Q', 'K', 'A'] or hole_card[1][1] in ['T', 'J', 'Q', 'K', 'A']:
      sample = rand.uniform(0,1)
      if sample <= .75:
        return 'call'
      return 'raise'
    return 'fold'

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
  return EvilPlayer()
