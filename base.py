from redpajama.core.quality_signals.base import RPSBase
from redpajama.core.data_types import SignalType

from collections import defaultdict

quality_signals_registry = defaultdict(dict)

# Register quality signals
def register_quality_signal(name, spec):
    def decorator(cls):
        assert name not in quality_signals_registry[spec]
        quality_signals_registry[spec][name] = cls
        return cls
    return decorator

class QSCodeBase(RPSBase):
    RPS_PREFIX: str = "QSC_"

