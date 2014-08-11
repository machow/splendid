from run import G

fname = 'test_save.pickle'
G.save(fname)
G2 = G.load(fname)
