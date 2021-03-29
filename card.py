CARD_EFFECTS = [
	# tier 0
	'f2r',

	# tier 1
	'upg110',
	'upg101',
	'p2r',
	'f2p',
	'b2v',
	'b2p',
	'convw',

	# tier 2
	'upg212',
	'bb2p',
	'bb2v',
	'convx2',
	'convw2',
	'pp2r',
	'bff2pp',
]
COLORS = [
	'r', 'g', 'b', 'y'
]

class Card:
	def __init__(self, idnum, tier, col, points, cost, eff, effcol1, effcol2):
		self.idnum = idnum
		self.tier = tier
		self.col = col
		self.points = points
		self.cost = cost
		self.eff = eff
		self.effcol1 = effcol1
		self.effcol2 = effcol2

class CardData:
	def __init__(self):
		self.tiers = [[], [], [], []]
		self.cards = []

	def parse(self, fname):
		with open(fname) as fin:
			line = fin.readline()
			cnt = 0
			curr_tier = 0
			while line:
				line = line.strip()
				if line == 'TIER0':
					curr_tier = 0
				elif line == 'TIER1':
					curr_tier = 1
				elif line == 'TIER2':
					curr_tier = 2
				elif line == 'TIER3':
					curr_tier = 3
				else:
					args = line.split()
					col = COLORS.index(args[0])
					points = int(args[1])
					cost = int(args[2])
					eff = CARD_EFFECTS.index(args[3])
					effcol1, effcol2 = None, None
					if CARD_EFFECTS[eff] in ['bb2v', 'bb2p', 'pp2r']:
						effcol1 = COLORS.index(args[4])
						effcol2 = COLORS.index(args[5])
					if CARD_EFFECTS[eff] in ['p2r', 'b2v', 'b2p', 'convw', 'convx2', 'convw2']:
						effcol1 = COLORS.index(args[4])
					curr_card_list = self.tiers[curr_tier]
					card = Card(cnt, curr_tier, col, points, cost, eff, effcol1, effcol2)
					curr_card_list += [card]
					self.cards += [card]
					cnt += 1

				line = fin.readline()
