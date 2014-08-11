import csv
from splendid.classes import LandDeck
def decks_from_csv(fname):
    """generate decks from CSV. Must contain the columns..

    id:         unique int identifier
    cost:       gem costs (str, e.g. 'rrgb')
    type:       color gem supplies
    tier:       level of deck (e.g. 1,2,3)
    pv:         point value

    """
    land_data = []
    tiers_set = set()
    for row in csv.DictReader(open(fname, 'rU')):
        cost = {k:int(v) for k, v in row.iteritems() if len(k) == 1}
        kwargs = {k:int(v) for k, v in row.iteritems() if k in ('id', 'pv', 'tier')}
        kwargs['cost'] = cost
        kwargs['type'] = row['type']
        land_data.append(kwargs)

        tiers_set.add(kwargs['tier'])
        

    decks = []
    for ii in range(1, len(tiers_set)+1):
        lands = filter(lambda d: d['tier'] == ii, land_data)
        decks.append(LandDeck(tier=ii, max_on_table=4, lands=lands))

    return decks
