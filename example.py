from pypokerengine.api.game import setup_config, start_poker
from random_player import RandomPlayer
from raise_player import RaisedPlayer
from tree_player import TreePlayer
from stump_player import StumpPlayer
from evil_player import EvilPlayer
from smart_player import SmartPlayer
from Group11Player import Group11Player

#TODO:config the config as our wish
config = setup_config(max_round=1000, initial_stack=10000, small_blind_amount=10)

config.register_player(name="smart", algorithm=SmartPlayer())
config.register_player(name="evil jr.", algorithm=Group11Player([0.9933917020855741, 0.13334717067544244, 0.4620091814940997, 0.7103040813536201, 0.6990725237608156, 0.4746825021396892, 0.36848530202169694, 0, 2]))

game_result = start_poker(config, verbose=0)
print(game_result)