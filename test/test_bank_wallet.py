from splendid.classes import Bank, Wallet

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

    def B_check_neg_good(gem_str): assert B.check_neg(gem_str)
    def B_check_neg_bad(gem_str): assert not B.check_neg(gem_str)

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



#B_full = Bank(gems = "".join([letter * 5  for letter in 'rbgwb']))
#Wallet()
