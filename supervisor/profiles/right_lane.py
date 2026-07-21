from highway_env.envs.highway_env import HighwayEnv

from supervisor.profiles.abstract import AbstractNormProfile
from supervisor.norms.constraints import CollisionConstraint
from supervisor.norms.norms import (
    LanePreference,
    LaneKeepingNorm
)

class RightLaneNormProfile(AbstractNormProfile):
    """Profile for right-lane driving norms."""
    LANE_PREFERENCE = LanePreference.RIGHT # Preferred lane for right-lane driving

    def __init__(self, env: HighwayEnv):
        """Initialize the right-lane driving profile with norms."""
        super().__init__(
            constraints=[
                CollisionConstraint(
                    min_ttc=(1 / env.config['policy_frequency'])
                )
            ],
            norms=[
                LaneKeepingNorm(
                    lane_preference=type(self).LANE_PREFERENCE,
                    weight=1
                )
            ]
        )
