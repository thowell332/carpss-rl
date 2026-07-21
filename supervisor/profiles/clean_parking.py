from highway_env.envs.parking_env import ParkingEnv

from supervisor.profiles.abstract import AbstractNormProfile
from supervisor.norms.norms import AvoidParkingLinesNorm

class CleanParkingNormProfile(AbstractNormProfile):
    """Profile for parking without touching the parking lines."""
    def __init__(self, env: ParkingEnv):
        """Initialize the right-lane driving profile with norms.
        
        :param policy_frequency: the policy frequency (Hz).
        :param simulation_frequency: the simulation frequency (Hz).
        """
        super().__init__(
            constraints=[],
            norms=[
                AvoidParkingLinesNorm(
                    policy_frequency=env.config['policy_frequency'],
                    simulation_frequency=env.config['simulation_frequency'],
                    weight=1
                )
            ]
        )
