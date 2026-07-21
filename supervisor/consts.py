"""Shared supervisor constants and action mappings.

This module centralizes constants that are used across the supervisor package,
including:

- ``VEHICLE_LENGTH``: length of the MDPVehicle used in the HighwayEnv environments.
- ``ACTION_STRINGS``: mapping from action label (e.g., ``"FASTER"``) to the
  corresponding discrete action index used by ``DiscreteMetaAction``.
"""

from highway_env.envs.common.action import DiscreteMetaAction
from highway_env.vehicle.controller import MDPVehicle

# Public constants

#: Vehicle length for convenience when computing following distances.
VEHICLE_LENGTH: float = MDPVehicle.LENGTH

#: Mapping from action label to discrete action index, e.g. ``"FASTER" -> 3``.
ACTION_STRINGS: dict[str, int] = {
    label: idx for idx, label in DiscreteMetaAction.ACTIONS_ALL.items()
}


