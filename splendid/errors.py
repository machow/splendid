class MoveError(Exception):
    codes = {
    101: "taking gems produces defecit (value is neg gems)",
    102: "can't draw two (value is valid draw2 options)",
    103: "invalid draw type (e.g. even before checks. value is str)",
    104: "can't buy land with gem amount (str)",
    105: "tried to reserve land not on table or can't afford (str)",
    106: "tried to reserve a land, but already have 3 reservations"
    }
    def __init__(self, code, value=None, text=None):
        self.code = code
        self.value = value
        if not text: self.text = self.codes[code]
        else: self.text = text

    def __str__(self):
        return repr(self.value)
