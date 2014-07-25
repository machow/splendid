from splendid.classes import Bank, Wallet, Game, LandDeck
import yaml
import csv
config = yaml.load(open('config.yaml'))

#W = Wallet()
#B = Bank(config['bank'])

land_data = []
for row in csv.DictReader(open('misc/lands.csv', 'rU')):
    cost = {k:int(v) for k, v in row.iteritems() if len(k) == 1}
    kwargs = {k:int(v) for k, v in row.iteritems() if k in ('id', 'pv', 'tier')}
    kwargs['cost'] = cost
    kwargs['type'] = row['type']
    land_data.append(kwargs)

decks = []
for ii in range(1, 4):
    lands = filter(lambda d: d['tier'] == ii, land_data)
    decks.append(LandDeck(tier=ii, max_on_table=4, lands=lands, shuffle=False))
    

G = Game(2, config['bank'], decks, config['cmd_dict'])

print G.decks[0]
print G.bank
print G.decks[0].deck[0]
print G._players[0]
