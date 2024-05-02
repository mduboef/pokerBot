from pypokerengine.players import BasePokerPlayer
import gametree as gt
import handprobability as handProb
import timeit


#IDEA: Make an agent that doesn't think very hard, all it does is look at the odds of win/loss/tie and
#raise/fold/call depending on which is the highest. Does not seem to work.

class StumpPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    handOdds = handProb.getWinLossTieOdds(hole_card, round_state['community_card'], 50, 5000)['WinLossTie']
    #print(handOdds)
    if handOdds[0] > handOdds[1] and handOdds[0] > handOdds[2]:
      return 'raise'
    if handOdds[1] > handOdds[0] and handOdds[1] > handOdds[2]:
      print('FOLD')
      return 'fold'
    if handOdds[2] > handOdds[0] and handOdds[2] > handOdds[1]:
      return 'call'
    return 'call'#action_choice

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
  return StumpPlayer()
