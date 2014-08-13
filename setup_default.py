from splendid.classes import Bank, Wallet, Game, LandDeck
from splendid.tools import decks_from_csv

import yaml
config = yaml.load(open('config.yaml'))

decks = decks_from_csv('misc/lands.csv')
nobles = decks_from_csv('misc/nobles.csv')[0]

G = Game(config['bank'], decks, nobles, config['cmd_dict'])
import pickle
pickle.dump(G, open('game_default.pickle', 'wb'))
pickle.dump([config['bank'], decks, nobles, config['cmd_dict']], open('game_args.pickle', 'wb'))
