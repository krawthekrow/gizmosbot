from card import *
from gizmos import *
from gui import *
from ai import *
import random

if __name__ == '__main__':
	card_data = CardData()
	card_data.parse('card_data.txt')
	engine = Gizmos(card_data)
	random_ai = RandomAi()
	single_move_ai = SingleMoveAi()
	mcts_ai = NaiveMcts()
	gui = GizmosGui(engine)
	gui.print_game_state()
	while engine.turn < 20:
		# move = mcts_ai.choose_move(engine)
		move = single_move_ai.choose_move(engine)
		# move = random_ai.choose_move(engine)

		engine.run_move(move)
		print()
		print()
		print('-- %s --' % gui.get_move_string(move))
		print()
		gui.print_game_state()
	print()
	print()
	print('final score = %d' % engine.calc_score())
