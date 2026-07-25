from scipy.optimize import bisect
from scipy.optimize import RootResults
from torch.distributions import Categorical
from torch.distributions.kl import kl_divergence
from typing import Tuple
import math
import torch

from highway_env.envs.common.action import Action, DiscreteMetaAction
from stable_baselines3 import DQN

from supervisor.abstract import (
    AbstractSupervisor,
    FloatArray1D,
    PolicyAugmentMethod,
    PolicyAugmentOutcome
)
from supervisor.profiles.abstract import AbstractNormProfile
from supervisor.profiles.right_lane import RightLaneNormProfile
from supervisor.profiles.merge_courtesy import MergeCourtesyNormProfile

class DiscreteSupervisor(AbstractSupervisor):
    """RCPS supervisor class for the discrete action space HighwayEnv environment."""
    PROFILES: dict[str, type[AbstractNormProfile]] = {
        'right_lane': RightLaneNormProfile,
        'merge_courtesy': MergeCourtesyNormProfile,
    }
    ACTIONS_ALL = DiscreteMetaAction.ACTIONS_ALL # Discrete action mapping

    # @override (commented out for backwards compatibility with python<3.12)
    def _get_model_policy(self, model: DQN, obs: FloatArray1D) -> torch.Tensor:
        """Return the action probabilities from the DQN model for the given observation.
        
        :param model: DQN model.
        :param obs: observation from the environment.
        :return: policy over the action space as a torch Tensor.
        """
        obs_tensor = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
        with torch.no_grad():
            q_tensor     = model.q_net(obs_tensor)     # Shape: (1, num_actions)
            probs_tensor = torch.softmax(q_tensor, dim=-1)

        action_probs = probs_tensor.squeeze(0)         # Shape: (num_actions,)
        if self.verbose:
            print("Model policy probabilities:")
            for action, prob in enumerate(action_probs):
                print(f"  {self.ACTIONS_ALL[action]}: {prob:.3f}")
        return action_probs
    
    def _apply_rcps_update(
        self,
        log_policy_support: torch.Tensor,
        cost_support: torch.Tensor,
        eta: float
    ) -> torch.Tensor:
        """Update the policy support based on the hyperparameter eta.
        
        :param log_policy_support: precomputed policy support in log space.
        :param cost_support: norm violation costs over the policy support.
        :param eta: hyperparameter for the KL-divergence estimation, where eta = log(beta).
        :return: [policy * exp(-cost / beta)] / Z (normalized).
        """
        beta = torch.exp(torch.tensor(eta, device=self.device))
        logits = log_policy_support - cost_support / beta
        logits -= torch.max(logits)
        updated_policy_support = torch.exp(logits)
        updated_policy_support /= torch.sum(updated_policy_support)
        return updated_policy_support
    
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
        zero = torch.zeros_like(policy)
        support_mask = ~torch.isclose(policy, zero)
        policy_support = policy[support_mask]
        one = torch.ones((), device=policy_support.device, dtype=policy_support.dtype)
        if not torch.isclose(policy_support.sum(), one):
            raise ValueError(f"Policy support does not sum to 1: {policy_support.sum():.4f}")

        # Cache cost vector for use in all computations
        cost = self.get_norm_violation_cost(self.ACTIONS_ALL)
        cost_support: torch.Tensor = cost[support_mask]
        if self.verbose:
            print(f"Cost vector:")
            for action, cost in enumerate(cost):
                print(f"  {self.ACTIONS_ALL[action]}: {cost:.3f}")
        
        # Return the original policy if the cost function is uniform
        if torch.allclose(cost_support, cost_support[0]):
            if self.verbose:
                print(f"All actions are equally norm compliant! No augmentation needed.")
            return policy, None, PolicyAugmentOutcome.UNCHANGED

        # Compute greedy projection onto the minimum cost action space
        if method in [PolicyAugmentMethod.ADAPTIVE, PolicyAugmentMethod.PROJECTION]:
            min_cost_mask = torch.isclose(cost_support, torch.min(cost_support))
            updated_policy_support = policy_support * min_cost_mask
            updated_policy_support /= torch.sum(updated_policy_support)
            kl_value = kl_divergence(
                Categorical(probs=updated_policy_support),
                Categorical(probs=policy_support)
            ).item()
            # Always return the greedy policy for the PROJECTION method or for the ADAPTIVE method
            # if the KL budget is satisfied.
            if (method == PolicyAugmentMethod.PROJECTION
                or (method == PolicyAugmentMethod.ADAPTIVE and kl_value <= self.kl_budget)):
                # Construct updated policy from new support
                updated_policy = torch.full_like(policy, 0.0, device=self.device)
                updated_policy[support_mask] = updated_policy_support
                if self.verbose:
                    print(f"Updated policy KL-divergence: {kl_value:.3f}")
                    print("Updated policy:")
                    for action, prob in enumerate(updated_policy):
                        print(f"  {self.ACTIONS_ALL[action]}: {prob:.3f}")
                return updated_policy, None, PolicyAugmentOutcome.PROJECTION

        # Cache log policy support for use in subsequent computations
        log_policy_support = torch.log(policy_support)

        # Normalize cost support for numerical stability
        # NOTE: This is especially important for the fixed beta method
        normalized_cost_support = cost_support / torch.sum(cost_support)

        # Used fixed beta provided by the user
        if method == PolicyAugmentMethod.FIXED:
            eta_star     = math.log(self.fixed_beta)
            root_results = None
        # Or solve for eta=log(beta) using root-finding algorithm
        elif method == PolicyAugmentMethod.ADAPTIVE:
            def kl_gap(eta: float) -> float:
                """Return the difference between the KL-divergence induced by eta and the budget."""
                updated_policy_support \
                    = self._apply_rcps_update(log_policy_support, normalized_cost_support, eta)
                kl_value = kl_divergence(
                    Categorical(probs=updated_policy_support),
                    Categorical(probs=policy_support)
                ).item()
                return kl_value - self.kl_budget

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

        # Update policy support
        updated_policy_support \
            = self._apply_rcps_update(log_policy_support, normalized_cost_support, eta_star)
        if self.verbose:
            print(f"Best Estimate: {eta_star:.3f}")

        # Construct updated policy from new support
        updated_policy = torch.full_like(policy, 0.0, device=self.device)
        updated_policy[support_mask] = updated_policy_support
        if self.verbose:
            kl_value = kl_divergence(
                Categorical(probs=updated_policy_support),
                Categorical(probs=policy_support)
            ).item()
            print(f"Updated policy KL-divergence: {kl_value}")
            print("Updated policy:")
            for action, prob in enumerate(updated_policy):
                print(f"  {self.ACTIONS_ALL[action]}: {prob:.3f}")

        return updated_policy, root_results, PolicyAugmentOutcome.RCPS_AUGMENTED
    
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
        cost = self.get_norm_violation_cost(self.ACTIONS_ALL)

        # Return the original policy if the cost function is uniform
        if torch.allclose(cost, cost[0]):
            if self.verbose:
                print(f"All actions are equally norm compliant! No augmentation needed.")
            return policy, PolicyAugmentOutcome.UNCHANGED

        normalized_cost = cost / torch.sum(cost)
        updated_policy = policy * (1.0 / (1.0 + normalized_cost))
        updated_policy /= torch.sum(updated_policy)
        return updated_policy, PolicyAugmentOutcome.NAIVELY_AUGMENTED
    
    def _get_permissibility_mask(self) -> torch.Tensor:
        """Return a boolean mask over the action space indicating permissible actions.

        :return: boolean mask over the action space as a torch Tensor.
        """
        constraint_violations = torch.zeros(
            len(self.ACTIONS_ALL),
            dtype=torch.int32,
            device=self.device
        )
        for action in self.ACTIONS_ALL.keys():
            for constraint in self.profile.constraints:
                constraint_violations[action] \
                    += int(constraint.is_violating_action(self.env.vehicle, action))

        return (constraint_violations == torch.min(constraint_violations))

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
        if not enforce_constraints:
            if self.verbose:
                print("Not enforcing constraints! Selecting from shaped policy.")
            return int(shaped_policy.argmax().detach().cpu().item())

        mask = self._get_permissibility_mask()
        selection_policy = shaped_policy
        # Prefer the shaped policy over the soft-permissible set when it has mass there.
        # Otherwise fall back to the unshaped policy over the cost-minimal permissible set,
        # so the selected action is still minimum-cost among soft-permissible actions.
        if torch.sum(shaped_policy[mask]) <= 0:
            if self.verbose:
                print(
                    "Shaped policy has no mass on soft-permissible actions; "
                    "falling back to unshaped policy over the cost-minimal permissible set."
                )
            cost = self.get_norm_violation_cost(self.ACTIONS_ALL)
            mask = mask & torch.isclose(cost, torch.min(cost[mask]))
            selection_policy = unshaped_policy

        policy_filtered = torch.zeros_like(shaped_policy)
        support = selection_policy[mask]
        policy_filtered[mask] = support / torch.sum(support)
        if self.verbose:
            print("Filtered Model Policy Probabilities:")
            for action, prob in enumerate(policy_filtered):
                print(f"  {self.ACTIONS_ALL[action]}: {prob:.3f}")

        return int(policy_filtered.argmax().detach().cpu().item())
