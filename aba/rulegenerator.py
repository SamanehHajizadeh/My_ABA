class RuleGenerator(dict):
    def __init__(self, symbols, result=None):
        dict.__init__(self, symbols=symbols, result=result)

        self.symbols = symbols
        self.result = result

    def __str__(self):
        """
        Meaning that set of symbols can derive result
        """
        if None in self.symbols:
            return "|- " + self.result
        return ", ".join(self.symbols) + " |- " + self.result
