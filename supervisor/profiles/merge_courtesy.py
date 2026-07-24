from highway_env.envs.common.abstract import AbstractEnv

from supervisor.profiles.abstract import AbstractNormProfile
from supervisor.norms.constraints import CollisionConstraint
from supervisor.norms.norms import MergeCourtesyNorm


class MergeCourtesyNormProfile(AbstractNormProfile):
    """Profile for merge-courtesy norms on the MergeEnv family."""

    #: Courtesy envelope length behind the merger [m].
    # Forecast gap under each action (get_next_speed); SLOWER lessens cost without
    # a hard exclusion. 90m ≈ two seconds at 30 m/s; keep residual
    # MergeEnvMEAddCourtesyReward.courtesy_distance in sync.
    COURTESY_DISTANCE = 90.0
    #: Highway lane id the ramp vehicle merges into (MergeEnv: 1 = right).
    TARGET_LANE_ID = 1

    def __init__(self, env: AbstractEnv):
        """Initialize the merge-courtesy profile with hard constraints and norms."""
        super().__init__(
            constraints=[
                CollisionConstraint(
                    min_ttc=(1 / env.config["policy_frequency"])
                )
            ],
            norms=[
                MergeCourtesyNorm(
                    courtesy_distance=type(self).COURTESY_DISTANCE,
                    target_lane_id=type(self).TARGET_LANE_ID,
                    policy_frequency=float(env.config["policy_frequency"]),
                    weight=1,
                )
            ],
        )
