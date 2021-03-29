import random
from card import *
import itertools

class Gizmos:
	def __init__(self, card_data, init=True):
		self.card_data = card_data

		if init:
			self.reset()

	def add_to_built(self, card):
		card_d = self.card_data.cards[card]
		self.built_by_eff[card_d.eff] += [card]
		self.card_vp += card_d.points

	def draw_card_from_tier(self, tier):
		deck = self.tier_decks[tier]
		if len(deck) == 0:
			return None
		if self.simulation:
			card_i = random.randint(0, len(deck) - 1)
			return deck.pop(card_i)
		return deck.pop()

	def get_random_hidden(self):
		cumsum = list(itertools.accumulate(self.hidden_marbles))
		rand = random.randint(0, cumsum[-1] - 1)
		for i, thres in enumerate(cumsum):
			if rand < thres:
				return i
		raise Exception('out of marbles')

	def dispense_marble(self):
		if self.visible_marble is not None:
			self.pickable_marbles[self.visible_marble] += 1

		col = self.get_random_hidden()
		self.visible_marble = col
		self.hidden_marbles[col] -= 1

	def reset(self):
		self.illegal_move = False
		self.simulation = False

		self.tier_decks = [[card.idnum for card in cards] for cards in self.card_data.tiers]
		for i in range(4):
			random.shuffle(self.tier_decks[i])
		self.tier_decks[3] = self.tier_decks[3][:16]

		self.tier_showns = [[], [None, None, None, None], [None, None, None], [None, None]]
		for tier in range(4):
			for i in range(len(self.tier_showns[tier])):
				self.tier_showns[tier][i] = self.draw_card_from_tier(tier)

		self.built_by_eff = [[] for eff in CARD_EFFECTS]
		self.archive = []

		self.hidden_marbles = [13, 13, 13, 13]
		self.pickable_marbles = [0, 0, 0, 0]
		self.visible_marble = None

		for i in range(7):
			self.dispense_marble()

		self.inv_marbles = [0, 0, 0, 0]

		self.marble_cap = 5
		self.file_cap = 1
		self.research_cap = 3

		self.card_vp = 0
		self.vp = 0

		self.add_to_built(self.card_data.tiers[0][0].idnum)

		self.turn = 0
		self.reset_turn()

	def reset_turn(self):
		self.pending_generic = 1
		self.pending_picks = 0
		self.pending_rands = 0
		self.tapped_by_eff = [[0 for card in cards] for cards in self.built_by_eff]

	def sim_clone(self):
		ogame = Gizmos(self.card_data, init=False)
		ogame.illegal_move = self.illegal_move
		ogame.simulation = True
		ogame.tier_decks = [deck.copy() for deck in self.tier_decks]
		ogame.tier_showns = [showns.copy() for showns in self.tier_showns]
		ogame.built_by_eff = [cards.copy() for cards in self.built_by_eff]
		ogame.archive = self.archive.copy()
		ogame.hidden_marbles = self.hidden_marbles.copy()
		ogame.pickable_marbles = self.pickable_marbles.copy()
		ogame.visible_marble = self.visible_marble
		ogame.inv_marbles = self.inv_marbles.copy()
		ogame.marble_cap = self.marble_cap
		ogame.file_cap = self.file_cap
		ogame.research_cap = self.research_cap
		ogame.card_vp = self.card_vp
		ogame.vp = self.vp
		ogame.turn = self.turn
		ogame.pending_generic = self.pending_generic
		ogame.pending_picks = self.pending_picks
		ogame.pending_rands = self.pending_rands
		ogame.tapped_by_eff = [tapped.copy() for tapped in self.tapped_by_eff]
		return ogame

	def get_i_card_tapped_it(self, eff):
		# note that tapped might be shorter than built if a card is
		# just built -- ignore that card in this iterator
		return enumerate(zip(self.built_by_eff[eff], self.tapped_by_eff[eff]))

	def card_has_effcol(self, card, col):
		card_d = self.card_data.cards[card]
		return (card_d.effcol1 is not None and card_d.effcol1 == col) or (card_d.effcol2 is not None and card_d.effcol2 == col)

	# API
	def new_turn(self):
		self.reset_turn()
		self.turn += 1

	def can_pick(self, col):
		return self.pickable_marbles[col] > 0

	def pick_is_legal(self, col):
		if self.pending_generic <= 0 and self.pending_picks <= 0:
			return False
		if sum(self.inv_marbles) >= self.marble_cap:
			return False
		if self.pickable_marbles[col] <= 0:
			return False
		return True

	# API
	def pick(self, col):
		if not self.pick_is_legal(col):
			illegal_move = True
			return
		if self.pending_picks == 0:
			self.pending_generic -= 1
		else:
			self.pending_picks -= 1

		self.pickable_marbles[col] -= 1
		self.dispense_marble()
		self.inv_marbles[col] += 1

		p2r_i = CARD_EFFECTS.index('p2r')
		for i, (card, tapped) in self.get_i_card_tapped_it(p2r_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.pending_rands += 1
				self.tapped_by_eff[p2r_i][i] += 1

		pp2r_i = CARD_EFFECTS.index('pp2r')
		for i, (card, tapped) in self.get_i_card_tapped_it(pp2r_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.pending_rands += 1
				self.tapped_by_eff[pp2r_i][i] += 1

	def draw_marble_is_legal(self):
		# assume there are enough marbles to draw
		if self.pending_rands <= 0:
			return False
		if sum(self.inv_marbles) >= self.marble_cap:
			return False
		return True

	# API
	def draw_marble(self):
		if not self.draw_marble_is_legal():
			illegal_move = True
			return
		self.pending_rands -= 1

		col = self.get_random_hidden()
		self.hidden_marbles[col] -= 1
		self.inv_marbles[col] += 1

	def file_shown_is_legal(self, tier, index):
		if self.pending_generic <= 0:
			return False
		if self.tier_showns[tier][index] is None:
			return False
		if len(self.archive) >= self.file_cap:
			return False
		return True

	# API
	def file_shown(self, tier, index):
		if not self.file_shown_is_legal(tier, index):
			illegal_move = True
			return
		self.pending_generic -= 1

		self.file_card(self.tier_showns[tier][index])

	def file_card(self, card_to_file):
		f2p_i = CARD_EFFECTS.index('f2p')
		for i, (card, tapped) in self.get_i_card_tapped_it(f2p_i):
			if tapped < 1:
				self.pending_picks += 1
				self.tapped_by_eff[f2p_i][i] += 1

		f2r_i = CARD_EFFECTS.index('f2r')
		for i, (card, tapped) in self.get_i_card_tapped_it(f2r_i):
			if tapped < 1:
				self.pending_rands += 1
				self.tapped_by_eff[f2r_i][i] += 1

		card = card_to_file

		self.archive += [card]

	def can_build(self, card):
		card_d = self.card_data.cards[card]
		return self.inv_marbles[card_d.col] >= card_d.cost

	def build(self, card_to_build):
		card_d = self.card_data.cards[card_to_build]
		col = card_d.col

		b2p_i = CARD_EFFECTS.index('b2p')
		for i, (card, tapped) in self.get_i_card_tapped_it(b2p_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.pending_picks += 1
				self.tapped_by_eff[b2p_i][i] += 1

		bb2p_i = CARD_EFFECTS.index('bb2p')
		for i, (card, tapped) in self.get_i_card_tapped_it(bb2p_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.pending_picks += 1
				self.tapped_by_eff[bb2p_i][i] += 1

		b2v_i = CARD_EFFECTS.index('b2v')
		for i, (card, tapped) in self.get_i_card_tapped_it(b2v_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.vp += 1
				self.tapped_by_eff[b2v_i][i] += 1

		bb2v_i = CARD_EFFECTS.index('bb2v')
		for i, (card, tapped) in self.get_i_card_tapped_it(bb2v_i):
			if tapped < 1 and self.card_has_effcol(card, col):
				self.vp += 1
				self.tapped_by_eff[bb2v_i][i] += 1

		card = card_to_build

		self.inv_marbles[card_d.col] -= card_d.cost
		self.add_to_built(card)
		if card_d.eff == CARD_EFFECTS.index('upg110'):
			self.marble_cap += 1
			self.file_cap += 1
		if card_d.eff == CARD_EFFECTS.index('upg101'):
			self.marble_cap += 1
			self.research_cap += 1
		if card_d.eff == CARD_EFFECTS.index('upg212'):
			self.marble_cap += 2
			self.file_cap + 1
			self.research_cap += 2

	def build_from_file_is_legal(self, index):
		if self.pending_generic <= 0:
			return False
		if index >= len(self.archive):	
			return False
		if not self.can_build(self.archive[index]):
			return False

	# API
	def build_from_file(self, index):
		if not self.build_from_file_is_legal(index):
			illegal_move = True
			return
		self.pending_generic -= 1

		bff2pp_i = CARD_EFFECTS.index('bff2pp')
		for i in range(len(self.built_by_eff[bff2pp_i])):
			card = self.built_by_eff[bff2pp_i][i]
			if self.tapped_by_eff[bff2pp_i][i] < 1:
				self.pending_picks += 2
				self.tapped_by_eff[bff2pp_i][i] += 1

		build(self.archive.pop(index))

	def build_from_shown_is_legal(self, tier, index):
		if self.pending_generic <= 0:
			return False
		if self.tier_showns[tier][index] is None:
			return False
		if not self.can_build(self.tier_showns[tier][index]):
			return False
		return True

	# API
	def build_from_shown(self, tier, index):
		if not self.build_from_shown_is_legal(tier, index):
			illegal_move = True
			return
		self.pending_generic -= 1

		self.build(self.tier_showns[tier][index])
		self.tier_showns[tier][index] = self.draw_card_from_tier(tier)

	def get_legal_moves(self):
		legal_moves = []

		legal_moves += [Move(MOVE_TYPES.index('new_turn'))]
		if self.draw_marble_is_legal():
			legal_moves += [Move(MOVE_TYPES.index('draw_marble'))]
		for i in range(4):
			if self.pick_is_legal(i):
				legal_moves += [Move(MOVE_TYPES.index('pick'), col=i)]
		for tier in range(4):
			for i in range(len(self.tier_showns[tier])):
				if self.file_shown_is_legal(tier, i):
					legal_moves += [Move(MOVE_TYPES.index('file_shown'), tier=tier, index=i)]
				if self.build_from_shown_is_legal(tier, i):
					legal_moves += [Move(MOVE_TYPES.index('build_from_shown'), tier=tier, index=i)]
		for i in range(len(self.archive)):
			if self.build_from_file_is_legal(i):
				legal_moves += [Move(MOVE_TYPES.index('build_from_file'), index=i)]
		return legal_moves

	# get the card built by the move
	def get_move_build(self, move):
		card = None
		if move.move_type == MOVE_TYPES.index('build_from_file'):
			card = self.archive[move.index]
		if move.move_type == MOVE_TYPES.index('build_from_shown'):
			card = self.tier_showns[move.tier][move.index]
		if card is None:
			return None
		return self.card_data.cards[card]

	def run_move(self, move, check_illegal=True):
		if move.move_type == MOVE_TYPES.index('new_turn'):
			self.new_turn()
		elif move.move_type == MOVE_TYPES.index('draw_marble'):
			self.draw_marble()
		elif move.move_type == MOVE_TYPES.index('pick'):
			self.pick(move.col)
		elif move.move_type == MOVE_TYPES.index('file_shown'):
			self.file_shown(move.tier, move.index)
		elif move.move_type == MOVE_TYPES.index('build_from_file'):
			self.build_from_file(move.index)
		elif move.move_type == MOVE_TYPES.index('build_from_shown'):
			self.build_from_shown(move.tier, move.index)

		if check_illegal and self.illegal_move:
			raise Exception('tried to run an illegal move')

	def calc_score(self):
		return self.vp + self.card_vp

MOVE_TYPES = [
	'new_turn',
	'draw_marble',
	'pick',
	'file_shown',
	'build_from_file',
	'build_from_shown'
]
class Move:
	def __init__(self, move_type, col=None, tier=None, index=None):
		self.move_type = move_type
		self.col = col
		self.tier = tier
		self.index = index
