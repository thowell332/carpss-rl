from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple
from scipy.optimize import RootResults
import numpy as np
import numpy.typing as npt
import torch

from highway_env.envs.common.abstract import Observation
from highway_env.envs.common.action import Action
from highway_env.envs.common.abstract import AbstractEnv
from stable_baselines3.common.base_class import BaseAlgorithm

from supervisor.profiles.abstract import AbstractNormProfile

# Type alias for 1D array of floating points
FloatArray1D = npt.NDArray[np.float64]
IntArray1D = npt.NDArray[np.int32]

class PolicyAugmentMethod(Enum):
    """Enum for supervisor methods."""
    NOP        = 'nop'        # No policy augment method applied.
    NAIVE      = 'naive'      # Naive augment rule
    FIXED      = 'fixed'      # Use a fixed beta value
    ADAPTIVE   = 'adaptive'   # Adaptively calculate beta based on KL budget
    PROJECTION = 'projection' # Project policy onto the minimum cost action space

class PolicyAugmentOutcome(Enum):
    """Enum for policy augment outcomes."""
    UNCHANGED         = 'unchanged'         # Original policy returned
    NAIVELY_AUGMENTED = 'naively_augmented' # Policy naively augmented
    RCPS_AUGMENTED    = 'rcps_augmented'    # Policy augmented using RCPS
    PROJECTION        = 'projection'        # Cost-optimal projection returned

class AbstractSupervisor(ABC):
    """Abstract RCPS supervisor class for the highway-env environment."""
    PROFILES = {} # Must be defined by the derived class

    def __init__(
        self,
        env: AbstractEnv,
        profile_name: str,
        method: str = PolicyAugmentMethod.ADAPTIVE.value,
        enforce_constraints: bool = True,
        fixed_beta: Optional[float] = 1.0,
        kl_budget: Optional[float] = 0.01,
        eta_max: Optional[float] = 10.0,
        eta_min: Optional[float] = -10.0,
        tol: Optional[float] = 1e-4,
        device: Optional[torch.device] = None,
        verbose=False
    ) -> None:
        """Initialize the supervisor with the environment and configuration.

        :param env: the unwrapped environment.
        :param profile_name: the name of the norm profile to use for the supervisor.
        :param method: the method for policy augmentation ('fixed', 'adaptive', 'naive', 'nop').
        :param enforce_constraints: whether to enforce hard constraints by projection.
        :param fixed_beta: fixed beta value for the supervisory policy.
            This value is only used for the FIXED method.
        :param kl_budget: maximum KL-divergence for the supervisory policy.
            This value is only used for the ADPATIVE method.
        :param eta_max: maximum value for the KL-divergence hyperparameter (eta=log(beta)).
            This value is only used for the ADPATIVE method.
        :param eta_min: minimum value for the KL-divergence hyperparameter (eta=log(beta)).
            This value is only used for the ADPATIVE method.
        :param tol: tolerance for the KL-divergence estimation.
            This value is only used for the ADPATIVE method.
        :param device: torch device to use for computations.
        :param verbose: whether to print debug information.
            This value is only used for the ADPATIVE method.
        """
        # Ensure proper enum types can be constructed from string parameters
        try:
            self.profile_name = profile_name.lower()
            self.profile: AbstractNormProfile = self.PROFILES[self.profile_name](env)
        except KeyError:
            raise ValueError(f"Invalid profile: {profile_name}. Expected one of "
                             f"{[p for p in self.PROFILES.keys()]}")
        try:
            self.method = PolicyAugmentMethod(method.lower())
        except ValueError:
            raise ValueError(f"Invalid method: {method}. Expected one of "
                             f"{[m.value for m in PolicyAugmentMethod]}")
        
        # Ensure internal consistency of specified parameters
        if self.method == PolicyAugmentMethod.FIXED and fixed_beta is None:
            raise ValueError("fixed_beta must be provided for the 'fixed' method!")
        
        if self.method == PolicyAugmentMethod.ADAPTIVE and any(
            param is None for param in [kl_budget, eta_max, eta_min, tol]
        ):
            raise ValueError("kl_budget, eta_max, eta_min, and tol must be provided for the "
                             "'adaptive' method!")
        
        # Check for value ranges
        if self.method == PolicyAugmentMethod.ADAPTIVE and kl_budget <= 0:
            raise ValueError("kl_budget must be greater than zero for the 'adaptive' method!")

        if self.method == PolicyAugmentMethod.ADAPTIVE and tol <= 0:
            raise ValueError("tol must be greater than zero for the 'adaptive' method!")
        
        if self.method == PolicyAugmentMethod.FIXED and fixed_beta <= 0:
            raise ValueError("fixed_beta must be greater than zero for the 'adaptive' method!") 

        self.env                 = env
        self.enforce_constraints = enforce_constraints
        self.fixed_beta          = fixed_beta
        self.kl_budget           = kl_budget
        self.eta_max             = eta_max
        self.eta_min             = eta_min
        self.tol                 = tol
        self.device              = device or (torch.device("cuda") if torch.cuda.is_available()
                                              else torch.device("cpu")) # Prefer GPU if available
        self.verbose             = verbose

        # Keep track of root finding results for performance analysis
        self.root_results_history: list[RootResults] = []

        # Keep track of how the polcy is augmented at each step
        self.outcome_history: list[PolicyAugmentOutcome] = []

        self.reset_norms()

    def reset_norms(self) -> None:
        """Reset the norms for the current environment.
        
        This method must be called every time the environment is reset to update the norm checkers
        with the new state of the environment.
        """
        self.norms      = self.profile.norms
        # Create a dictionary mapping norm names to their weights for easy access
        self.norm_weights = {str(norm): norm.weight for norm in self.norms}

    def calculate_norm_violation_costs(self, action: Action) -> dict[str, float]:
        """Return a dictionary mapping norms to violation costs for the given action."""
        violations_dict = {
            str(norm): norm.calculate_cost(self.env.vehicle, action)
            for norm in self.norms
        }
        return violations_dict

    def get_norm_violation_cost(self, actions: list[Action]) -> torch.Tensor:
        """Return the norm violation cost vector for the current state."""
        norm_violation_cost = torch.zeros(len(actions), device=self.device)
        for i, action in enumerate(actions):
            violations_cost = self.calculate_norm_violation_costs(action)
            # Apply norm weights to the violation costs
            weighted_violations = {norm: violations_cost[norm] * self.norm_weights[norm]
                                   for norm in violations_cost}
            norm_violation_cost[i] = sum(weighted_violations.values())

        return norm_violation_cost

    @abstractmethod
    def _get_model_policy(self, model: BaseAlgorithm, obs: FloatArray1D) -> torch.Tensor:
        """Get the model policy for the given observation.

        :param model: base RL model.
        :param obs: observation from the environment.
        :param args: additional arguments.
        :param kwargs: additional keyword arguments.
        :return: policy over the action space as a torch Tensor.
        """
        pass
    
    @abstractmethod
    def _augment_policy_rcps(
        self,
        policy: torch.Tensor,
        method: PolicyAugmentMethod
    ) -> Tuple[torch.Tensor, RootResults, PolicyAugmentOutcome]:
        """Augment the given policy using the specified RCPS method.

        The augmented policy is computed using either the 'fixed', 'adaptive', or 'projection'
        method. The 'fixed' method uses the provided beta_fixed value to compute the new policy,
        while the 'adaptive' method computes the value for beta to satisfy the KL-divergence
        constraint. In 'projection' mode, the cost-optimal projection is returned.

        :param policy: original policy to be augmented.
        :param method: the RCPS method to use for policy augmentation.
        :return: a tuple containing:
            - the augmented policy as a torch Tensor,
            - the root finding results from the KL-divergence estimation,
            - the policy augment outcome as a PolicyAugmentOutcome enum.
        """
        pass
    
    @abstractmethod
    def _augment_policy_naive(
        self,
        policy: torch.Tensor
    ) -> Tuple[torch.Tensor, PolicyAugmentOutcome]:
        """Naively augment the given policy to minimize the expected norm violation cost.
        
        This method simply multiplies the policy by 1/(1 + cost) to bias probabilities towards
        norm-compliant actions. It does not enforce any constraint on the KL-divergence.

        :param policy: original policy to be augmented.
        :return: a tuple containing:
            - the augmented policy as a torch Tensor,
            - the policy augment outcome as a PolicyAugmentOutcome enum.
        """
        pass

    def shape(self, model: BaseAlgorithm, obs: Observation) -> torch.Tensor:
        """Shapes the model policy with the configured policy augment method.
        
        :param model: base RL model.
        :param obs: observation from the environment.
        :return: shaped policy as a Torch tensor.
        """
        if model.device != self.device:
            raise RuntimeError(f"Expected model device ({model.device}) to match supervisor device "
                               f"({self.device})!")
        
        policy = self._get_model_policy(model, obs)
        outcome = PolicyAugmentOutcome.UNCHANGED
        
        # Augment the policy based on the supervisor mode
        if self.method == PolicyAugmentMethod.NOP:
            pass
        elif self.method == PolicyAugmentMethod.NAIVE:
            policy, outcome = self._augment_policy_naive(policy)
        elif self.method in [
            PolicyAugmentMethod.ADAPTIVE,
            PolicyAugmentMethod.FIXED,
            PolicyAugmentMethod.PROJECTION
        ]:
            policy, root_results, outcome = self._augment_policy_rcps(policy, self.method)
            self.root_results_history.append(root_results) # Keep track of root finding results
        else:
            raise ValueError(f"Unknown supervisor method: {self.method}")
        self.outcome_history.append(outcome) # Keep track of policy augment outcomes
        return policy

    @abstractmethod
    def decide(self, policy: torch.Tensor, enforce_constraints: bool = True) -> Action:
        """Select the final action based on the augmented policy.

        :param policy: the augmented policy as a torch Tensor.
        :param enforce_constraints: whether to enforce hard constraints by projection.
        :return: final action selection.
        """
        pass

    def predict(self, model: BaseAlgorithm, obs: Observation) -> Action:
        """Returns the supervised action selection for the given observation.

        :param model: base RL model.
        :param obs: observation from the environment.
        :return: final action selection.
        """
        return self.decide(self.shape(model, obs), self.enforce_constraints)

    @staticmethod
    def print_obs(obs: Observation):
        """Print kinematic observation data for the ego vehicle and all other present vehicles."""
        _, ego_x, ego_y, ego_vx, ego_vy = obs[0]
        print(f"Ego Vehicle: x={ego_x}, y={ego_y}, vx={ego_vx}, vy={ego_vy}")

        for presence, x, y, vx, vy in obs[1:]:
            if presence:
                print(f"Vehicle: x={x}, y={y}, vx={vx}, vy={vy}")
