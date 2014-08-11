from splendid.classes import Game
from splendid.tools import decks_from_csv
import yaml
config = yaml.load(open('config.yaml'))

decks = decks_from_csv('misc/lands.csv')
nobles = decks_from_csv('misc/nobles.csv')[0]

G = Game(config['bank'], decks, nobles, config['cmd_dict'])
G.start(['player1', 'player2'], shuffle=False) 

print "STRING TEST"
print G.decks[0]
print G.bank
print G.decks[0].deck[0]
print G._players[0]
print "\n\n"

G('do_draw', 'rr')
print G
G('do_draw', 'WW')
G('do_draw', 'Brg')
G('do_draw', 'BB')
G('do_buy', '40 Brrrg')
G._players[0].wallet.gems.update('r'*10 + 'b'*10 + 'B'*10 + 'g'*10 + 'W'*10)
G('draw', 'rr')
G('buy', '39 rbbWW')
G('reserve', '90')
for land in G.decks[0].deck:
    if land.type == 'W': G._players[0].lands.append(land)
for land in G.decks[0].deck:
    if land.type == 'B': G._players[0].lands.append(land)
