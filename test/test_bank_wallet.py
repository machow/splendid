from splendid.classes import Bank, Land, Wallet

# Test draws are well-formed --------------------------------------------------
def test_check_draw():
    good = ['bb', 'abc']
    bad = ['b', 'ab', 'bbb', 'bbbb', 'abcd',  'abb']

    def check_draw_good(gem_str): assert Bank.check_draw(gem_str)
    def check_draw_bad(gem_str): assert not Bank.check_draw(gem_str)

    for entry in good:
        yield check_draw_good, entry
    for entry in bad:
        yield check_draw_bad, entry

# Test does not go negative ---------------------------------------------------
def test_check_neg():
    B = Bank(gems = {'r': 0, 'g':2, 'b': 1, 'w': 1})
    good = ['gbw', 'gg', 'ggbw']
    bad =  ['r', 'rg', 'ggg']

    def B_check_neg_good(gem_str): assert not B.check_neg(gem_str)
    def B_check_neg_bad(gem_str): assert B.check_neg(gem_str)

    for entry in good:
        yield B_check_neg_good, entry
    for entry in bad:
        yield B_check_neg_bad, entry

# Test draw2 rule -------------------------------------------------------------
def test_draw2_rule():
    B = Bank(gems = {'r': 5, 'g':4, 'b': 3, 'w': 2, 'd':1})
    good = ['rr', 'gg',
            'r',  'g' ,
            'rgb', 'bwd']   # should return options here
    bad  = ['bb', 'ww', 'dd', 'b', 'w', 'd']
    # take into account case where no draw2 options and, say, rgb is given?

    def check_can_draw2_good(gem_str): assert B.check_can_draw2(gem_str)
    def check_can_draw2_bad(gem_str):  assert not B.check_can_draw2(gem_str)

    for entry in good:
        yield check_can_draw2_good, entry
    for entry in bad:
        yield check_can_draw2_bad, entry

# Test Land.check_can_buy -----------------------------------------------------
def check_can_buy_good(L, gem_str, base=None): assert L.check_can_buy(gem_str, base)
def check_can_buy_bad(L, gem_str, base=None): assert not L.check_can_buy(gem_str, base)

def test_check_can_buy_nobase():
    L = Land(id=0, cost='bbg', type='b', pv=0)
    good = ['bbg', 'bbA', 'bAg', 'Abg', 'AAA']
    bad  = [ 'bg',  'bA', 'bbb']

    for gem_str in good:
        yield check_can_buy_good, L, gem_str

    for gem_str in bad:
        yield check_can_buy_bad, L, gem_str

def test_check_can_buy_base():
    """Buy Land: for one gem, more base gems then cost"""
    L = Land(id=0, cost='bbg', type='b', pv=0)
    base = 'ggg'
    good = ['bb', 'bA', 'AA']
    bad  = ['b', 'bbb', 'bbg', 'bgA', 'AAA']

    for gem_str in good:
        yield check_can_buy_good, L, gem_str, base

    for gem_str in bad:
        yield check_can_buy_bad, L, gem_str, base
    
def test_check_can_buy_base2():
    """Buy land: for many blue cost, one base gem"""
    L = Land(id=0, cost='bbg', type='b', pv=0)
    base = 'b'
    good = ['bg', 'Ag', 'bA', 'AA']
    bad  = ['b', 'g', 'bbg']

    for gem_str in good:
        yield check_can_buy_good, L, gem_str, base

    for gem_str in bad:
        yield check_can_buy_bad, L, gem_str, base

def test_check_can_buy_base_free():
    """Buy land: so much gem action it's free"""
    L = Land(id=0, cost='bbg', type='b', pv=0)
    base = 'bbbggg'
    bad = ['b', 'bb', 'bbg', 'A']
    
    yield check_can_buy_good, L, '', base
    for gem_str in bad:
        yield check_can_buy_bad, L, gem_str, base

#------------------------------------------------------------------------------
# Test take methods on Bank, Wallet
#------------------------------------------------------------------------------

def test_bank_draw2():
    B = Bank('aaaaa')
    B.take('aa')
    assert B.gems['a'] == 3

def test_bank_draw3():
    B = Bank('rgb')
    B.take('rgb')
    assert sum(B.gems.values()) == 0

def test_bank_draw1_wild():
    B = Bank('A')
    B.take('A')
    assert B.gems['A'] == 0

def test_bank_draw1_notwild():
    B = Bank('Ab')
    # can't remember hwo to expect an exception
    #Bank.take('b')
    

def test_wallet_take():
    W = Wallet('rbgg')
    W.take('rbg')
    assert sum(W.gems.values()) == 1
    assert W.gems['g'] == 1

def test_wallet_put():
    W = Wallet('rbgg')
    W.put('rb')
    assert W.gems['r'] == 2
    assert W.gems['b'] == 2
