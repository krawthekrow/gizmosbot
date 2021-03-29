from card import *
from gizmos import *

class GizmosGui:
	def __init__(self, engine):
		self.engine = engine

	def get_card_string(self, card):
		card_d = self.engine.card_data.cards[card]
		effcol1 = '' if card_d.effcol1 is None else COLORS[card_d.effcol1]
		effcol2 = '' if card_d.effcol2 is None else COLORS[card_d.effcol2]
		effcols = '' if card_d.effcol1 is None and card_d.effcol2 is None else ('_%s%s' % (effcol1, effcol2))
		return '%s%d%d_%s%s' % (COLORS[card_d.col], card_d.points, card_d.cost, CARD_EFFECTS[card_d.eff], effcols)

	def print_game_state(self):
		print('[%s]' % COLORS[self.engine.visible_marble], end='')
		for col, num in zip(COLORS, self.engine.pickable_marbles):
			for _ in range(num):
				print(' %s' % col, end='')
		print()
		print()

		for tier in range(1, 4):
			print('[%d]' % len(self.engine.tier_decks[tier]), end='')
			for card in self.engine.tier_showns[tier]:
				print(' %s' % ('emp' if card is None else self.get_card_string(card)), end='')
			print()
		print()

		print('turn = %d' % self.engine.turn)
		print('vp = %d' % self.engine.vp)
		print('pending picks = %d' % self.engine.pending_picks)
		print('pending rands = %d' % self.engine.pending_rands)
		print('[inv]', end='')
		for col, num in zip(COLORS, self.engine.inv_marbles):
			for _ in range(num):
				print(' %s' % col, end='')
		print()
		print('[file]', end='')
		for card in self.engine.archive:
			print(' %s' % self.get_card_string(card), end='')
		print()

		for tappeds, cards in zip(self.engine.tapped_by_eff, self.engine.built_by_eff):
			if len(cards) == 0:
				continue
			print('|', end='')
			for i, card in enumerate(cards):
				print(' %s' % self.get_card_string(card), end='')
				if i < len(tappeds):
					for _ in range(tappeds[i]):
						print('*', end='')
			print()
		print()

	def get_move_string(self, move):
		col = '' if move.col is None else (' %s' % COLORS[move.col])
		tier = '' if move.tier is None else (' tier=%d' % move.tier)
		index = '' if move.index is None else (' i=%s' % move.index)
		return '%s%s%s%s' % (MOVE_TYPES[move.move_type], col, tier, index)
