from splendid.classes import Moves, Player, LandDeck, Bank
M = Moves()

# Test do_draw ---------------------------------------------------------------
class test_move:
    def setup(self):
        self.P = Player('joe')
        self.P.wallet.put('rgb')
        self.B = Bank('rrrrggA')
        lands = [dict(id=ii, cost='r'*ii,type='B', pv=ii) for ii in range(1,6)]
        lands.reverse()
        self.decks = [LandDeck(1, 4, lands=lands, shuffle=False)]

    def test_do_draw_gems_conserved(self):
        # has one r, adds 2
        M.do_draw('rr', self.B, self.P)
        assert self.P.wallet.gems['r'] == 3
        assert self.B.gems['r'] == 2

    def test_do_buy(self):
        L = self.decks[0].take(1)
        M.do_buy(1, 'r', self.B, self.decks, self.P)
        assert self.P.lands[0] is L
        assert self.P.lands[0].owner == self.P.name
        assert self.P.wallet.gems['r'] == 0
        assert L in self.decks[0].elsewhere
        assert L not in self.decks[0].table

    def test_do_reserve(self):
        L = self.decks[0].take(1)
        M.do_reserve(1, self.B, self.decks, self.P)
        assert self.P.reserve[0] is L
        assert self.P.reserve[0].owner is None
        assert self.P.wallet.gems['A'] == 1
