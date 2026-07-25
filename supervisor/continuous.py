from typing import Optional, Tuple
from scipy.optimize import bisect
from scipy.optimize import RootResults
from torch.distributions import Normal, Independent
import torch
import math

from highway_env.envs.common.action import Action
from highway_env.envs.common.abstract import AbstractEnv
from stable_baselines3 import SAC
from stable_baselines3.sac.policies import Actor

from supervisor.abstract import (
    AbstractSupervisor,
    FloatArray1D,
    PolicyAugmentMethod,
    PolicyAugmentOutcome
)
from supervisor.profiles.abstract import AbstractNormProfile
from supervisor.profiles.clean_parking import CleanParkingNormProfile

class ContinuousSupervisor(AbstractSupervisor):
    """RCPS supervisor class for the continuous action space HighwayEnv environment."""
    PROFILES: dict[str, type[AbstractNormProfile]] = {
        'clean_parking': CleanParkingNormProfile
    }

    def __init__(
        self,
        env: AbstractEnv,
        profile_name: str,
        method: str = PolicyAugmentMethod.ADAPTIVE.value,
        enforce_constraints: bool = True,
        fixed_beta: Optional[float] = 1.0,
        kl_budget: Optional[float] = 0.01,
        eta_max: Optional[float] = 100.0,
        eta_min: Optional[float] = -10.0,
        tol: Optional[float] = 1e-4,
        k_samples: Optional[int] = 1024,
        min_rstd: Optional[float] = 0.1,
        device: Optional[torch.device] = None,
        verbose=False
    ) -> None:
        """Initialize the supervisor with the environment and configuration.

        :param env: the unwrapped environment.
        :param profile_name: the name of the norm profile to use for the supervisor.
        :param enforce_constraints: whether to enforce hard constraints by projection.
        :param method: the method for policy augmentation ('fixed', 'adaptive', 'naive', 'nop').
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
        :param k_samples: number of action samples to draw from the SAC policy.
        :param min_rstd: minimum standard deviation for the reshaped action distribution relative
            to the original SAC policy standard deviation.
        :param device: torch device to use for computations.
        :param verbose: whether to print debug information.
            This value is only used for the ADPATIVE method.
        """
        super().__init__(
            env,
            profile_name,
            method,
            enforce_constraints,
            fixed_beta,
            kl_budget,
            eta_max,
            eta_min,
            tol,
            device,
            verbose
        )
        self.k_samples = k_samples
        self.min_rstd = min_rstd
        
    # @override (commented out for backwards compatibility with python<3.12)
    def _get_model_policy(self, model: SAC, obs: FloatArray1D) -> torch.Tensor:
        """Return the mean and std of the action distribution from the SAC model for the given observation.
        
        :param model: SAC model.
        :param obs: observation from the environment.
        :return: mean and std of the action distribution as a torch Tensor.
        """
        obs_tensor = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            actor: Actor = model.actor
            mean, log_std, _ = actor.get_action_dist_params(obs_tensor)
            if mean.shape[0] != 1:
                raise ValueError(f"Expected batch size of 1, got {mean.shape[0]}!")
            
            mean = mean.squeeze(0)       # Shape: (act_dim,)
            log_std = log_std.squeeze(0) # Shape: (act_dim,)
            std = torch.exp(log_std)
            if self.verbose:
                print("Model policy distribution:")
                for dim in range(mean.shape[0]):
                    print(f"  Action Dim {dim}: mean={mean[dim]:.3f}, std={std[dim]:.3f}")
            return torch.stack([mean, std], dim=0) # Shape: (2, act_dim)
        
    def _sample_sac_actions(
        self,
        policy: torch.Tensor,
        k_samples: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Sample k actions from the SAC policy distribution.
        
        :param policy: SAC policy containing mean and std tensors.
        :param k_samples: number of action samples to draw.
        :return: tuple of unsquashed and squashed action samples as torch Tensors.
        """
        mean, std = policy
        if mean.shape != std.shape:
            raise ValueError(f"Mean and std shapes do not match: {mean.shape} vs {std.shape}!")
        action_dim = mean.shape[0]
        eps = torch.randn((k_samples, action_dim), device=self.device) # eps ~ N(0, I)
        unsquashed_actions = mean + eps * std                          # u ~ N(mean, std)
        if self.verbose:
            print("Unsquashed Action Samples:")
            for action in enumerate(unsquashed_actions):
                print(f"  {action}")

        squashed_actions = torch.tanh(unsquashed_actions)
        return unsquashed_actions, squashed_actions
    
    def _apply_rcps_update(
        self,
        std: float,
        unsquashed_actions: torch.Tensor,
        cost: FloatArray1D,
        eta: float
    ) -> torch.Tensor:
        """Update the policy support based on the hyperparameter eta.

        :param std: standard deviation of the original policy to be reshaped.
        :param unsquashed_actions: samples from the SAC policy distribution before squashing.
        :param cost: norm violation costs over the policy support.
        :param eta: hyperparameter for the KL-divergence estimation, where eta = log(beta).
        :return: mean and std of the reweighted action distribution as a torch Tensor.
        """
        weights: torch.Tensor = torch.softmax(-cost / math.exp(eta), dim=0)
        updated_mean = torch.sum(weights.unsqueeze(-1) * unsquashed_actions, dim=0)
        unsquashed_actions_centered = unsquashed_actions - updated_mean.unsqueeze(0)
        updated_var = torch.sum(weights.unsqueeze(-1) * unsquashed_actions_centered.pow(2), dim=0)
        # Add small constant for numerical stability and clamp to minimum relative std
        updated_std = torch.sqrt(updated_var + 1e-12).clamp_min(self.min_rstd * std)
        return torch.stack([updated_mean, updated_std], dim=0) # Shape: (2, act_dim)
    
    # @override (commented out for backwards compatibility with python<3.12)
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
        mean, std = policy
        unsquashed_actions, squashed_actions = self._sample_sac_actions(policy, self.k_samples)

        # Cache cost vector for use in all computations
        cost = self.get_norm_violation_cost(squashed_actions.detach().cpu().numpy())
        if self.verbose:
            print(f"Cost vector for squashed actions:")
            for action, cost in enumerate(cost):
                print(f"  {squashed_actions[action]}: {cost:.3f}")
        
        # Return the original policy if the cost function is uniform
        if torch.allclose(cost, cost[0]):
            if self.verbose:
                print(f"All actions are equally norm compliant! No augmentation needed.")
            return policy, None, PolicyAugmentOutcome.UNCHANGED
        
        # Normalize cost support for numerical stability
        # NOTE: This is especially important for the fixed beta method
        normalized_cost = cost / torch.sum(cost)

        # Approximate the greedy projection onto the minimum cost action space
        if method in [PolicyAugmentMethod.ADAPTIVE, PolicyAugmentMethod.PROJECTION]:
            updated_mean, updated_std \
                = self._apply_rcps_update(std, unsquashed_actions, normalized_cost, self.eta_min)
            updated_dist = Independent(Normal(updated_mean, updated_std), 1)
            original_dist = Independent(Normal(mean, std), 1)
            kl_value = torch.distributions.kl_divergence(updated_dist, original_dist)
            # Always return the greedy policy for the PROJECTION method or for the ADAPTIVE method
            # if the KL budget is satisfied.
            if (method == PolicyAugmentMethod.PROJECTION
                or (method == PolicyAugmentMethod.ADAPTIVE and kl_value <= self.kl_budget)):
                if self.verbose:
                    print(f"Updated policy KL-divergence: {kl_value:.3f}")
                    print("Updated policy distribution:")
                    for dim in range(updated_mean.shape[0]):
                        print(f"  Action Dim {dim}: mean={updated_mean[dim]:.3f}, std={updated_std[dim]:.3f}")
                return (torch.stack([updated_mean, updated_std], dim=0), None,
                        PolicyAugmentOutcome.PROJECTION)

        # Used fixed beta provided by the user
        if method == PolicyAugmentMethod.FIXED:
            eta_star = torch.log(self.fixed_beta, device=self.device)
        # Or solve for eta=log(beta) using root-finding algorithm
        elif method == PolicyAugmentMethod.ADAPTIVE:
            def kl_gap(eta: float) -> float:
                """Return the difference between the KL-divergence induced by eta and the budget."""
                updated_mean, updated_std \
                    = self._apply_rcps_update(std, unsquashed_actions, normalized_cost, eta)
                updated_dist = Independent(Normal(updated_mean, updated_std), 1)
                original_dist = Independent(Normal(mean, std), 1)
                kl_value = torch.distributions.kl_divergence(updated_dist, original_dist)
                return (kl_value - self.kl_budget).detach().cpu().numpy()

            # Require the function to be bracketed over the provided interval
            kl_gap_high = kl_gap(self.eta_min)
            kl_gap_low  = kl_gap(self.eta_max)
            if kl_gap_high * kl_gap_low > 0:
                raise ValueError(f"KL constraint not bracketed: [({self.eta_min}, {kl_gap_high:.4f}), "
                                f"({self.eta_max}, {kl_gap_low:.4f})]")
            
            eta_star, root_results = bisect(
                f=kl_gap,
                a=self.eta_min,
                b=self.eta_max,
                xtol=self.tol,
                full_output=True
            )
            if not root_results.converged:
                print(f"WARNING: KL-divergence estimation did not converge: {root_results.flag}")
        else:
            raise ValueError(f"Unknown supervisor method: {method}")

        # Update policy distribution
        updated_mean, updated_std = self._apply_rcps_update(std, unsquashed_actions, cost, eta_star)
        if self.verbose:
            print(f"Best Estimate: {eta_star:.3f}")
            updated_dist = Independent(Normal(updated_mean, updated_std), 1)
            original_dist = Independent(Normal(mean, std), 1)
            kl_value = torch.distributions.kl_divergence(updated_dist, original_dist)
            print(f"Updated policy KL-divergence: {kl_value}")
            print("Updated policy distribution:")
            for dim in range(mean.shape[0]):
                    print(f"  Action Dim {dim}: mean={mean[dim]:.3f}, std={std[dim]:.3f}")

        return (torch.stack([updated_mean, updated_std], dim=0), root_results,
                PolicyAugmentOutcome.RCPS_AUGMENTED)
    
    # @override (commented out for backwards compatibility with python<3.12)
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
        _, std = policy
        unsquashed_actions, squashed_actions = self._sample_sac_actions(policy, self.k_samples)

        # Cache cost vector for use in all computations
        cost = self.get_norm_violation_cost(squashed_actions)
        if self.verbose:
            print(f"Cost vector for squashed actions:")
            for action, cost in enumerate(cost):
                print(f"  {squashed_actions[action]}: {cost:.3f}")
        
        # Return the original policy if the cost function is uniform
        if torch.allclose(cost, cost[0]):
            if self.verbose:
                print(f"All actions are equally norm compliant! No augmentation needed.")
            return policy, None, PolicyAugmentOutcome.UNCHANGED
        
        # Normalize cost support for numerical stability
        normalized_cost = cost / torch.sum(cost)

        weights: torch.Tensor = unsquashed_actions * (1.0 / (1.0 + normalized_cost))
        updated_mean = torch.sum(weights.unsqueeze(-1) * unsquashed_actions, dim=0)
        unsquashed_actions_centered = unsquashed_actions - updated_mean.unsqueeze(0)
        updated_var = torch.sum(weights.unsqueeze(-1) * unsquashed_actions_centered.pow(2), dim=0)
        # Add small constant for numerical stability and clamp to minimum relative std
        updated_std = torch.sqrt(updated_var + 1e-12).clamp_min(self.min_rstd * std)
        return torch.stack([updated_mean, updated_std], dim=0) # Shape: (2, act_dim)

    # @override (commented out for backwards compatibility with python<3.12)
    def decide(
        self,
        unshaped_policy: torch.Tensor,
        shaped_policy: torch.Tensor,
        enforce_constraints: bool = True
    ) -> Action:
        """Select the final action based on the unshaped and shaped policies.

        :param unshaped_policy: the original model policy as a torch Tensor.
        :param shaped_policy: the augmented policy as a torch Tensor.
        :param enforce_constraints: whether to enforce hard constraints by projection.
        :return: final action selection.
        """
        if enforce_constraints:
            raise NotImplementedError("Constraint enforcement not implemented")
        
        mean, _ = shaped_policy
        return mean.numpy(force=True)
