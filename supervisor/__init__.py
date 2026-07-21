"""
RCPS Supervisor Package

A package for implementing Runtime Constrained Policy Shaping (RCPS) as a supervisor module in
the HighwayEnv driving environment.
"""

from .abstract import AbstractSupervisor, PolicyAugmentMethod, PolicyAugmentOutcome
from .discrete import DiscreteSupervisor
from .continuous import ContinuousSupervisor
from .consts import VEHICLE_LENGTH, ACTION_STRINGS

__version__ = "0.1.0"
__all__ = [
    "AbstractSupervisor",
    "PolicyAugmentMethod",
    "PolicyAugmentOutcome",
    "DiscreteSupervisor",
    "ContinuousSupervisor",
    "VEHICLE_LENGTH",
    "ACTION_STRINGS"
]
