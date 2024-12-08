from redpajama.core.quality_signals.base import RPSBase

from collections import defaultdict

quality_signals_registry = defaultdict(dict)

# quality signals register
def register_quality_signal(name, spec):
    def decorator(cls):
        assert name not in quality_signals_registry[spec]
        quality_signals_registry[spec][name] = cls
        return cls
    return decorator

class QSCodeBase(RPSBase):
    RPS_PREFIX: str = "QSC_"

