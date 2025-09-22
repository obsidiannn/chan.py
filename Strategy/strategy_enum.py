import enum


class StrategyEnum(enum.Enum):

    CHAN = 'strategy_chan', '策略:缠'

    def __init__(self, code, _name):
        self.code = code
        self._name = _name
