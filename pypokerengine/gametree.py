import itertools
import random

class PokerNode:
    def __init__(self, player, action=None, amount=0, pot=0, hole_cards=None, community_cards=None, parent=None, is_chance_node=False):
        self.player = player
        self.action = action
        self.amount = amount
        self.pot = pot
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.parent = parent
        self.is_chance_node = is_chance_node
        self.children = []

    def add_child(self, child):
        self.children.append(child)
