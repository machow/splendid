from errors import MoveError
from collections import Counter
class Wallet:
    def __init__(self, gems=None):
        """Takes dict {'r':5, 'b': 4, ...} or iterable to feed to Counter"""
        if type(gems) == dict: 
            self.gems = Counter("".join([k * v for k, v in gems.items()]))
        else: self.gems = Counter(gems)

    def put(self, gem_str):
        """Add gem_str to gems"""
        self.gems.update(gem_str)

    def take(self, gem_str, safe=True):
        """Remove gem_str from gems"""
        if safe: 
            assert not self.check_neg(gem_str) 

        self.gems.subtract(gem_str)

    def check_neg(self, gem_str, base=None, safe=False):
        """Returns a counter with defecits for overdrawn gems"""
        tmp = self.gems.copy() - Counter(base)
        tmp.subtract(gem_str)
        neg = {k:v for k, v in tmp.iteritems() if v < 0}

        if safe and neg:
            raise MoveError(101, neg)

        return neg

    def __str__(self):
        sorted_gems = sorted(self.gems.items(), key=lambda l: l[0])
        return " ".join([str(v) + k for k, v in sorted_gems]).replace('1','')

    def __repr__(self):
        return "Wallet({gems_str})".format(gems_str=str(self))

    @property
    def to_json(self): return self.gems

        
class Bank(Wallet):
    def take(self, gem_str, safe=True):
        """Remove gem_str from gems"""

        if safe: 
            self.check_draw(gem_str, safe=safe)
            self.check_neg(gem_str, safe=safe)
            self.check_can_draw2(gem_str, safe=safe)

        self.gems.subtract(gem_str)

    def check_can_draw2(self, gem_str=False, safe=False):
        """When given gem_str, returns False iff gem_str is invalid draw2 set
        
        If gem_str not given, returns string of valid draw2 gems
        """
        options = "".join([k for k, v in self.gems.iteritems() if v >= 4])
        options.replace('A', '')

        # return valid options when gem_str is false
        if not gem_str: return options
        elif len(gem_str) == 3: return True
        # check if single type of gem given is in options
        elif len(gem_str) == 1 or len(set(gem_str)) == 1: 
            good = gem_str[0] in (options + 'A')
            if safe and not good: raise MoveError(102, options)
            else: return good

    @staticmethod
    def check_draw(gem_str, safe=False):
        """Return True if gem_str follows rules of draw types"""
        # str is either 'A', 2 of one color, or 3 different colors
        unique = len(set(gem_str))
        good = (len(gem_str) == 1 and gem_str == 'A') or \
               (len(gem_str) == 2 and unique == 1) or \
               (len(gem_str) == unique == 3)
        if safe and not good: raise MoveError(103, 'invalid draw')
        
        return good
        

class Land:
    def __init__(self, id, cost, type, pv, owner=None, tier=None):
        """kwargs out of laziness, tier was put into spreadsheet, need to fix"""
        self.id = int(id)
        self.cost = Wallet(cost)

        self.type, self.pv, self.owner = type, pv, owner
        self.tier = tier

    def check_can_buy(self, gem_str, base=None, safe=False):
        """Return True if gem_str will pay for Land.cost AND is not excessive"""
        payment, base = Counter(gem_str), Counter(base)
        remain = self.cost.gems - base - payment     # this operation will not go neg
        ttl = sum(remain.values())
        # Checks
        enough_gems = payment['A'] == ttl
        neg = self.cost.check_neg(gem_str.replace('A', ''), base=base, safe=safe)

        if safe and not enough_gems: raise MoveError(104, remain)
        return enough_gems and not neg

    def __int__(self):
        """This allows a Land instance and land_id to be exchangable in methods"""
        return int(self.id)

    def __str__(self):
        return "[{id}]: {cost} | +{type} | pv: {pv}".format(id=self.id,
                                                 cost=self.cost,
                                                 type=self.type,
                                                 pv=self.pv)

    @property
    def to_json(self):
        data = {k:self.__dict__[k] for k in ['id', 'type', 'pv', 'owner', 'tier']}
        data['cost'] = self.cost.gems

        return data


import random
class LandDeck:
    """Used for each deck of lands. Cards are drawn from .deck to .table.
    
    Cards in player hands should go into .elsewhere"""
    def __init__(self, tier, max_on_table, lands=None):
        """Initialize, shuffle, draw first {max_on_table} cards"""
        self.tier = tier
        self._max_on_table = max_on_table
        self.table = []
        self.elsewhere = []
        
        if not lands: self.deck = []
        else: self.deck = [Land(**entry) for entry in lands]

    def deal(self):
        self.draw(self._max_on_table)

    def draw(self, n):
        """Move card from deck to table"""
        self.table.extend([self.deck.pop() for ii in range(n)])

    def shuffle_deck(self):
        """shuffle cards in deck in place"""
        random.shuffle(self.deck)

    def take(self, land_id, remove=False):
        """Return first (and hopefully only) land card matching land_id. Otherwise, None"""
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

    @property
    def to_json(self):
        out = {}
        for k in ['deck', 'table', 'elsewhere']:
            out[k] = [land.to_json for land in getattr(self, k)]
        out['tier'] = self.tier
        return out


class Moves:
    """Flyweight class for holding game actions. No non-method attributes"""

    def do_draw(self, gem_str, bank, player):
        bank.take(gem_str)
        player.wallet.put(gem_str)

    def do_reserve(self, land_id, bank, decks, player):
        if len(player.reserve) == 3: raise MoveError(106)
        for Deck in decks:
            L = Deck.take(land_id)
            if L:
                bank.take('A')
                player.wallet.put('A')
                Deck.take(land_id, remove=True)
                Deck.draw(1)
                player.reserve.append(L)
                break 
        else: raise MoveError(105, "no land with that id")

    def do_buy(self, land_id, gem_str, bank, decks,  player):
        for Deck in decks:
            L = Deck.take(land_id)
            if L and L.check_can_buy(gem_str, player.land_bonus):
                Deck.take(land_id, remove=True)
                player.wallet.take(gem_str)
                bank.put(gem_str)
                L.owner = player.name
                player.lands.append(L)
                Deck.draw(1)
                break
        else: raise MoveError(105, "no matching id or cannot afford") 

    def do_noble(self, noble_id, nobles, player):
        L = nobles.take(noble_id, remove=False)
        if not L:
            raise MoveError(105, "no matching id")
        elif L.check_can_buy("", player.land_bonus):
            nobles.take(noble_id, remove=True)
            L.owner = player.name
            player.nobles.append(L)
        else:
            raise MoveError(105, "cannot afford noble")
        
    
class Player:
    def __init__(self, name):
        self.name = name
        self.reserve = []
        self.wallet = Wallet()
        self.lands = []
        self.nobles = []

    @property
    def points(self): 
        land_points = sum([land.pv for land in self.lands])
        noble_points = sum([noble.pv for noble in self.nobles])
        return land_points + noble_points

    @property
    def land_bonus(self):
        gem_count = Counter()
        for land in self.lands: gem_count.update(land.type)
        return gem_count
        
    def __str__(self):
        stats =  "Player: {name} ({points}) | land bonus: {land_bonus} | gems: {wallet}"\
                    .format(name=self.name, points = self.points,
                            land_bonus=self.land_bonus, wallet=self.wallet)
        reserves = "        ".join(str(res) for res in self.reserve)
        return stats + '\n\t' + reserves

    @property
    def to_json(self):
        out = {}
        for k in ['reserve', 'lands', 'nobles']:
            out[k] = [land.to_json for land in getattr(self, k)]
        for k in ['name', 'points', 'land_bonus']:
            out[k] = getattr(self, k)
        out['gems'] = self.wallet.to_json

        return out


import inspect
import copy
import pickle
class Game(Moves):
    def __init__(self, bank, decks, nobles, cmd_dict=None, point_goal=15):
        self._hist = {}
        self._stages = (['do_draw', 'do_reserve', 'do_buy'],
                        ['do_noble']
                        )
        self.bank = Bank(bank)
        self.turn = 0
        self.decks = decks
        self.nobles = nobles
        self.cmd_dict = cmd_dict
        self.point_goal = point_goal

    def start(self, players, add_gems='', shuffle=True):
        self._players = [Player(name) for name in players]
        self.bank.put(add_gems)
        for deck in self.decks: 
            if shuffle: deck.shuffle_deck()
            deck.deal()
        if shuffle: self.nobles.shuffle_deck()
        self.nobles.deal()

        # Set up first round
        self.remaining_players = self._players[:]
        self.remaining_stages = self._stages[:]
        self.winner = None


    @property
    def crnt_player(self):
        return self.remaining_players[0]
    @property
    def crnt_stage(self):
        return self.remaining_stages[0]

    def __call__(self, cmd, string):
        """Submit turn for Game.

        Parameters:
            cmd: move from self._stages (can leave off do_)
            string: args to feed to cmd, split by spaces

        """
        if 'do_' not in cmd: cmd = 'do_' + cmd
        args = string.split(' ')
        crnt_stage = self.remaining_stages[0]
        if cmd in crnt_stage:
            # get command
            action = getattr(self, cmd)
            # inspect for bank or decks arguments
            funcsig = inspect.getargspec(action)[0]
            kwargs = {k: getattr(self, k) for k in ['bank', 'decks', 'nobles'] if k in funcsig}

            # call command
            action(*args, player=self.crnt_player, **kwargs)
            #print self.crnt_player

            self._next_stage()
            #print self.crnt_player
            #print self.bank
        else: raise BaseException('no') 

    def _next_stage(self):
        self.remaining_stages = self.remaining_stages[1:]
        
        print self.remaining_stages
        if self.remaining_stages:
            bonus = self.crnt_player.land_bonus
            rich = any(noble.check_can_buy("", bonus) for noble in self.nobles.table)
            print bonus
            if 'do_noble' in self.remaining_stages[0] and not rich:
                print 'too poor'
                self._next_stage()
        if not self.remaining_stages:
            self._next_player()
    
    def _next_player(self):
        self.remaining_stages = self._stages[:]
        self.remaining_players = self.remaining_players[1:]
        if not self.remaining_players:
            # move to next turn, reset player list
            self.turn += 1
            self.remaining_players = self._players[:]

            # check whether to end game
            player_points = {p.name:p.points for p in self._players}
            if any(points > self.point_goal for points in player_points.values()):
                # player(s) with highest points win
                highest = max(player_points.values())
                self.winner = filter(lambda p: p.points == highest, self._players)

        self.update_hist()


    def __str__(self):
        str_just = lambda land: str(land) + " "*(30 - len(str(land)))
        deck_strings = ["     ".join([str_just(land) for land in deck.table]) for deck in self.decks]
        noble_string = "     ".join([str_just(land) for land in self.nobles.table])
        stage = self.remaining_stages[0]

        return "\n\nTURN: {}     | MOVE: {}".format(self.crnt_player.name, stage) + \
               "\n\n==== PLAYERS ====\n" + "\n".join(str(p) for p in self._players) +\
               "\n\n==== BANK =====\n" + "\n" + str(self.bank) +\
               "\n\n==== LANDS ====\n" + "\n".join(deck_strings) +\
               "\n\n==== NOBLES ====\n" + noble_string

    def output(self, players='all'):
        """
        Parameters:
            players:    list of player names to include
        """
        out = {}

        if players == 'all': players = [p.name for p in self._players]
        out['players'] = {p.name: p.to_json for p in self._players if p.name in players}
        out['crnt_player'] = self.crnt_player.name
        out['crnt_move'] = self.remaining_stages[0]

        out['decks'] = []
        for deck in self.decks:
            tmp_json = deck.to_json
            out['decks'].append({k: tmp_json[k] for k in ['table', 'elsewhere', 'tier']})
        out['nobles'] = self.nobles.to_json['table']
        out['bank'] = self.bank.to_json
        out['winner'] = [p.to_json for p in (self.winner or [])]
        out['summary'] = str(self)

        return out

    @staticmethod
    def load(fname):
        """load pickeld game file"""
        return pickle.load(open(fname, 'rb'))

    def save(self, fname):
        """save game as pickled data in folder"""
        pickle.dump(self, open(fname, 'wb'))

    def update_hist(self):
        newG = copy.deepcopy(self)
        # Remove history so it doesn't become exp large
        newG._hist = {}
        playernum = self._players.index(self.crnt_player)
        key = "{turn}_{playernum}".format(turn=self.turn, playernum=playernum)
        self._hist[key] = newG
