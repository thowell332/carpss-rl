"""Merge-courtesy envelope geometry for residual add-on reward / SCPS dual.

Penetration ``x = clip((D - gap) / D, 0, 1)``; signals use ``sqrt(x)``.
Residual add-on uses actual gap; SCPS cost (in supervisor) uses predicted gap.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from highway_env.road.lane import AbstractLane
from highway_env.vehicle.kinematics import Vehicle

#: MergeEnv access-ramp nodes.
MERGE_NODES = frozenset({"j", "k"})

#: Default envelope length in vehicle lengths (matches MergeCourtesyNormProfile).
DEFAULT_COURTESY_DISTANCE_LENGTHS = 10.0


def is_merging_vehicle(other: Vehicle) -> bool:
    """True if ``other`` is on MergeEnv's ramp or dedicated merge lane."""
    lane_index = getattr(other, "lane_index", None)
    if lane_index is None:
        return False
    _from, _to, lane_id = lane_index
    if _from in MERGE_NODES or _to in MERGE_NODES:
        return True
    return (_from, _to) == ("b", "c") and lane_id >= 2


def merging_vehicles(ego: Vehicle) -> list[Vehicle]:
    return [
        other
        for other in ego.road.vehicles
        if other is not ego and is_merging_vehicle(other)
    ]


def envelope_penetration(gap: float, courtesy_distance: float) -> float:
    """Normalized courtesy-envelope violation in ``[0, 1]``."""
    if courtesy_distance <= 0:
        raise ValueError("courtesy_distance must be positive.")
    return float(np.clip((courtesy_distance - gap) / courtesy_distance, 0.0, 1.0))


def bumper_gap_on_lane(
    ego: Vehicle,
    merger: Vehicle,
    target_lane: AbstractLane,
) -> Optional[float]:
    """Bumper-to-bumper gap on ``target_lane``, or None if ego is ahead of merger.

    Requires ego behind or in line with the merger (``s_ego <= s_merge``).
    """
    s_ego, _ = target_lane.local_coordinates(ego.position)
    s_merge, _ = target_lane.local_coordinates(merger.position)
    if s_ego > s_merge:
        return None
    ego_front = s_ego + ego.LENGTH / 2.0
    merge_rear = s_merge - merger.LENGTH / 2.0
    return float(merge_rear - ego_front)


def max_actual_penetration(
    ego: Vehicle,
    courtesy_distance: float,
    target_lane_id: int = 1,
) -> float:
    """Max envelope penetration using the **actual** gap (state-based add-on).

    Returns 0 if courtesy is not applicable (no ramp merger, ego not on target
    lane, or ego ahead of all mergers).
    """
    if ego.lane_index[2] != target_lane_id:
        return 0.0
    mergers = merging_vehicles(ego)
    if not mergers:
        return 0.0

    _from, _to, _ = ego.lane_index
    try:
        target_lane = ego.road.network.get_lane((_from, _to, target_lane_id))
    except KeyError:
        return 0.0

    max_x = 0.0
    for merger in mergers:
        gap = bumper_gap_on_lane(ego, merger, target_lane)
        if gap is None:
            continue
        max_x = max(max_x, envelope_penetration(gap, courtesy_distance))
    return max_x


def courtesy_add_on_reward(
    ego: Vehicle,
    courtesy_distance: float,
    target_lane_id: int = 1,
) -> float:
    """Residual add-on: ``-sqrt(x)`` from actual gap; 0 when not violating."""
    if not getattr(ego, "on_road", True):
        return 0.0
    x = max_actual_penetration(ego, courtesy_distance, target_lane_id)
    if x <= 0.0:
        return 0.0
    return float(-np.sqrt(x))
