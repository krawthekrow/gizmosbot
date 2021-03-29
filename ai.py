import random
from gizmos import *

class RandomAi:
	def __init__(self):
		pass

	def choose_move(self, engine):
		return random.choice(engine.get_legal_moves())

class MoveScorer:
	def __init__(self):
		self.preferred_effs = [CARD_EFFECTS.index(eff) for eff in ['p2r', 'b2p', 'b2v', 'pp2r', 'bb2p', 'bb2v']]

	def get_scores(self, engine, moves):
		scores = [0 for _ in moves]

		new_turn_i = MOVE_TYPES.index('new_turn')
		draw_marble_i = MOVE_TYPES.index('draw_marble')
		build_from_file_i = MOVE_TYPES.index('build_from_file')
		build_from_shown_i = MOVE_TYPES.index('build_from_shown')
		for i, move in enumerate(moves):
			# don't end turn unnecessarily
			if len(moves) > 1 and move.move_type == new_turn_i:
				scores[i] -= 10000
			# don't draw when you can pick
			if engine.pending_picks > 0 and move.move_type == draw_marble_i:
				scores[i] -= 10000
			# prefer to build when possible
			if move.move_type == build_from_file_i or move.move_type == build_from_shown_i:
				scores[i] += 10

			# prefer pick and build cards
			card = engine.get_move_build(move)
			if card is not None and card.eff in self.preferred_effs:
				scores[i] += 5

		return scores

class SingleMoveAi:
	def __init__(self):
		self.scorer = MoveScorer()

	def choose_move(self, engine):
		legal_moves = engine.get_legal_moves()
		scores = self.scorer.get_scores(engine, legal_moves)
		_, best_i = max(zip(scores, range(len(scores))))
		return legal_moves[best_i]

class NaiveMcts:
	def __init__(self):
		self.move_scorer = MoveScorer()
		self.sim_ai = SingleMoveAi()
		self.sim = None

	def run_sim(self):
		while self.sim.turn < 20:
			self.sim.run_move(self.sim_ai.choose_move(self.sim))

	def choose_move(self, engine):
		legal_moves = engine.get_legal_moves()
		move_scores = self.move_scorer.get_scores(engine, legal_moves)
		scores = [0 for move in legal_moves]
		for i, move in enumerate(legal_moves):
			if move_scores[i] < 0:
				continue
			for _ in range(100):
				self.sim = engine.sim_clone()
				self.run_sim()
				scores[i] += self.sim.calc_score()
		_, best_i = max(zip(scores, range(len(scores))))
		return legal_moves[best_i]
