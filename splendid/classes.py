from collections import Counter
class Wallet:
    def __init__(self, gems=None):
        """Takes dict {'r':5, 'b': 4, ...} or iterable to feed to Counter"""
        if type(gems) == dict: 
            self.gems = Counter("".join([k * v for k, v in gems.items()]))
        else: self.gems = Counter(gems)

    def put(self, gem_str):
        self.gems.update(gem_str)

    def take(self, gem_str, safe=True):
        if safe: 
            assert self.check_neg(gem_str) 

        self.gems.subtract(gem_str)

    def check_neg(self, gem_str, base=None):
        tmp = self.gems.copy() - Counter(base)
        tmp.subtract(gem_str)
        neg = [v < 0 for k, v in tmp.iteritems()]
        return not any(neg)

    def __str__(self):
        return "".join([k * v for k, v in self.gems.iteritems()])
        
class Bank(Wallet):
    __name__ = 'Bank'
    def take(self, gem_str, safe=True):

        if safe: 
            assert self.check_draw(gem_str)
            assert self.check_neg(gem_str)
            assert self.check_can_draw2()

        self.gems.subtract(gem_str)

    def check_can_draw2(self, gem_str=False):
        options = "".join([k for k, v in self.gems.iteritems() if v >= 4])

        # check if single type of gem given is in options
        if gem_str and len(set(gem_str)) == 1: 
            return gem_str[0] in options
        # otherwise, just return options
        return options

    @staticmethod
    def check_draw(gem_str):
        # str is either 'A', 2 of one color, or 3 different colors
        unique = len(set(gem_str))
        return (len(gem_str) == 1 and gem_str == 'A') or \
               (len(gem_str) == 2 and unique == 1) or \
               (len(gem_str) == unique == 3)
        

class Game:
    def __init__(self, n_play, bank, decks, cmd_dict=None):
        self._players = [Player(ii) for ii in range(n_play)]
        self.bank = Bank(bank)
        self.turn = 0
        self.decks = decks
        self._stages = (['do_draw', 'do_reserve', 'do_buy'],
                        )
        self.cmd_dict = cmd_dict

        # Set up first round
        self.remaining_players = self._players[:]
        self.remaining_stages = self._stages[:]

    @property
    def crnt_player(self):
        return self.remaining_players[0]
    @property
    def crnt_stage(self):
        return self.remaining_stages[0]

    def __call__(self, cmd, string):
        args = string.split(' ')
        crnt_stage = self.remaining_stages[0]
        if cmd in crnt_stage:
            action = getattr(self, cmd)
            action(*args, player=self.crnt_player)
            print self.crnt_player

            self._next_stage()
            print self.crnt_player
            print self.bank
        else: BaseException('no') 

    def _next_stage(self):
        self.remaining_stages = self.remaining_stages[1:]
        if not self.remaining_stages:
            self._next_player()
    
    def _next_player(self):
        self.remaining_stages = self._stages[:]
        self.remaining_players = self.remaining_players[1:]
        if not self.remaining_players:
            self.turn += 1
            self.remaining_players = self._players[:]

    def do_draw(self, gem_str, player):
        self.bank.take(gem_str)
        player.wallet.put(gem_str)

    def do_reserve(self, land_id, player):
        self.bank.take('A')
        player.wallet.put('A')
        for Deck in self.decks:
            L = Deck.take(land_id)
            if L:
                Deck.take(land_id, remove=True)
                Deck.draw(1)
                player.reserve.append(L)
                break 

    def do_buy(self, land_id, gem_str, player):
        for Deck in self.decks:
            L = Deck.take(land_id)
            if L and L.check_can_buy(gem_str, player.land_bonus):
                Deck.take(land_id, remove=True)
                player.wallet.take(gem_str)
                self.bank.put(gem_str)
                L.owner = player.name
                player.lands.append(L)
                Deck.draw(1)
                break
        else: BaseException("no matching id or cannot afford") 

    def do_noble(self, nobel_id, player):
        pass
        
class Player:
    def __init__(self, name):
        self.name = name
        self.reserve = []
        self.wallet = Wallet()
        self.lands = []

    @property
    def points(self): 
        return sum([land.pv for land in self.lands])

    @property
    def land_bonus(self):
        gem_count = Counter()
        for land in self.lands: gem_count.update(land.type)
        return gem_count
        
    def __str__(self):
        return "Player: {name} ({points}) | land bonus: {land_bonus} | gems: {wallet}"\
                    .format(name=self.name, points = self.points,
                            land_bonus=self.land_bonus, wallet=self.wallet)

class Land:
    def __init__(self, id, cost, type, pv, **kwargs):
        """kwargs out of laziness, tier was put into spreadsheet, need to fix"""
        self.id = id
        self.cost, self.type, self.pv = Wallet(cost), type, pv
        self.owner = None

    def check_can_buy(self, gem_str, base=None):
        payment, base = Counter(gem_str), Counter(base)
        remain = self.cost.gems - base - payment     # this operation will not go neg
        ttl = sum(remain.values())
        if payment['A'] >= ttl and self.cost.check_neg(gem_str, base=None):
            return True
        else: 
            return False

    def __str__(self):
        return "[{id}]: {cost} | +{type}".format(id=self.id,
                                                 cost=self.cost,
                                                 type=self.type)

    def __int__(self):
        return int(self.id)


import random
class LandDeck:
    def __init__(self, tier, max_on_table, lands=None, shuffle=True):
        self.tier = tier
        self._max_on_table = max_on_table
        self.table = []
        self.elsewhere = []
        
        if not lands: self.deck = []
        else: self.deck = [Land(**entry) for entry in lands]

        if shuffle: self.shuffle_deck()

        self.draw(max_on_table)

    def draw(self, n):
        self.table.extend([self.deck.pop() for ii in range(n)])

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def take(self, land_id, remove=False):
        land_id = int(land_id)
        for ii, L in enumerate(self.table):
            if L.id == land_id:
                if remove:
                    self.table.pop(ii)
                    self.elsewhere.append(L)
                return L

    def __str__(self):
        return "<Tier {tier} Deck: {deck} / {table} / {elsewhere}>"\
                .format(tier = self.tier, deck = len(self.deck),
                        table = len(self.table), elsewhere = len(self.elsewhere))
