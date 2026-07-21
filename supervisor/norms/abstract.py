from abc import ABC, abstractmethod

from highway_env.envs.common.action import Action
from highway_env.vehicle.kinematics import Vehicle

class AbstractConstraint(ABC):
    """Abstract base class for constraints."""

    @abstractmethod
    def is_violating_action(self, vehicle: Vehicle, action: Action, *args, **kwargs) -> bool:
        """Check if the provided action violates the constraint in the vehicle's current state.
        
        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: True if the provided action is constraint-violating, False otherwise.
        """
        pass
    
    def __str__(self):
        """To string function."""
        pass

class AbstractNorm(AbstractConstraint):
    """Abstract base class for norms as weighted soft constraints."""

    def __init__(self, weight: float = 1.0) -> None:
        """Initialize the norm with a weight.

        :param weight: weight of the norm (default is 1.0).
        """
        if weight < 0:
            raise ValueError("Norm weight must be non-negative.")

        self.weight = weight
    
    def calculate_cost(self, vehicle: Vehicle, action: Action, *args, **kwargs) -> float:
        """Calculate the cost associated with this norm for the specified action.
        
        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :param *args: additional positional arguments for violation checking.
        :param **kwargs: additional keyword arguments for violation checking.
        :return: the cost associated with this norm for the specified action.
        """
        return 1.0 if self.is_violating_action(vehicle, action, *args, **kwargs) else 0.0
