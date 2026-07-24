import numpy as np
try:
    from gymnasium.envs.registration import register as register_gymnasium
except ImportError:
    register_gymnasium = None
try:
    from gym.envs.registration import register as register_gym
except ImportError:
    register_gym = None

from highway_env import utils
from highway_env.envs.common.abstract import AbstractEnv
from highway_env.road.lane import LineType, StraightLane, SineLane
from highway_env.road.road import Road, RoadNetwork
from highway_env.vehicle.controller import ControlledVehicle
from highway_env.vehicle.objects import Obstacle


class MergeEnv(AbstractEnv):

    """
    A highway merge negotiation environment.

    The ego-vehicle is driving on a highway and approached a merge, with some vehicles incoming on the access ramp.
    It is rewarded for maintaining a high speed and avoiding collisions, but also making room for merging
    vehicles.
    """

    @classmethod
    def default_config(cls) -> dict:
        cfg = super().default_config()
        cfg.update({
            "collision_reward": -1,
            "right_lane_reward": 0.1,
            "high_speed_reward": 0.2,
            "merging_speed_reward": -0.5,
            "lane_change_reward": -0.05,
            # Randomize NPC highway / ramp spawns each reset (seeded via env.reset).
            "highway_vehicles": 5,
            "spawn_longitude_jitter": 12.0,  # meters
            "spawn_speed_jitter": 1.5,       # m/s
            "min_spawn_gap": 10.0,           # bumper gap along-lane [m]
            "spawn_jitter_retries": 25,
        })
        return cfg

    def _reward(self, action: int) -> float:
        """
        The vehicle is rewarded for driving with high speed on lanes to the right and avoiding collisions

        But an additional altruistic penalty is also suffered if any vehicle on the merging lane has a low speed.

        :param action: the action performed
        :return: the reward of the state-action transition
        """
        action_reward = {0: self.config["lane_change_reward"],
                         1: 0,
                         2: self.config["lane_change_reward"],
                         3: 0,
                         4: 0}
        reward = self.config["collision_reward"] * self.vehicle.crashed \
            + self.config["right_lane_reward"] * self.vehicle.lane_index[2] / 1 \
            + self.config["high_speed_reward"] * self.vehicle.speed_index / (self.vehicle.target_speeds.size - 1)

        # Altruistic penalty
        for vehicle in self.road.vehicles:
            if vehicle.lane_index == ("b", "c", 2) and isinstance(vehicle, ControlledVehicle):
                reward += self.config["merging_speed_reward"] * \
                          (vehicle.target_speed - vehicle.speed) / vehicle.target_speed

        return utils.lmap(action_reward[action] + reward,
                          [self.config["collision_reward"] + self.config["merging_speed_reward"],
                           self.config["high_speed_reward"] + self.config["right_lane_reward"]],
                          [0, 1])

    def _is_terminal(self) -> bool:
        """The episode is over when a collision occurs or when the access ramp has been passed."""
        return self.vehicle.crashed or self.vehicle.position[0] > 370

    def _reset(self) -> None:
        self._make_road()
        self._make_vehicles()

    def _make_road(self) -> None:
        """
        Make a road composed of a straight highway and a merging lane.

        :return: the road
        """
        net = RoadNetwork()

        # Highway lanes
        ends = [150, 80, 80, 150]  # Before, converging, merge, after
        c, s, n = LineType.CONTINUOUS_LINE, LineType.STRIPED, LineType.NONE
        y = [0, StraightLane.DEFAULT_WIDTH]
        line_type = [[c, s], [n, c]]
        line_type_merge = [[c, s], [n, s]]
        for i in range(2):
            net.add_lane("a", "b", StraightLane([0, y[i]], [sum(ends[:2]), y[i]], line_types=line_type[i]))
            net.add_lane("b", "c", StraightLane([sum(ends[:2]), y[i]], [sum(ends[:3]), y[i]], line_types=line_type_merge[i]))
            net.add_lane("c", "d", StraightLane([sum(ends[:3]), y[i]], [sum(ends), y[i]], line_types=line_type[i]))

        # Merging lane
        amplitude = 3.25
        ljk = StraightLane([0, 6.5 + 4 + 4], [ends[0], 6.5 + 4 + 4], line_types=[c, c], forbidden=True)
        lkb = SineLane(ljk.position(ends[0], -amplitude), ljk.position(sum(ends[:2]), -amplitude),
                       amplitude, 2 * np.pi / (2*ends[1]), np.pi / 2, line_types=[c, c], forbidden=True)
        lbc = StraightLane(lkb.position(ends[1], 0), lkb.position(ends[1], 0) + [ends[2], 0],
                           line_types=[n, c], forbidden=True)
        net.add_lane("j", "k", ljk)
        net.add_lane("k", "b", lkb)
        net.add_lane("b", "c", lbc)
        road = Road(network=net, np_random=self.np_random, record_history=self.config["show_trajectories"])
        road.objects.append(Obstacle(road, lbc.position(ends[2], 0)))
        self.road = road

    def _make_vehicles(self) -> None:
        """
        Populate the highway and merge ramp with ego plus jittered NPC traffic.

        Ego is fixed for a stable evaluation geometry. Highway NPCs and the
        merging vehicle are placed near nominal slots with seeded longitudinal
        and speed noise so ``reset(seed=…)`` yields distinct episodes.
        """
        road = self.road
        rng = self.np_random

        ego_lane = road.network.get_lane(("a", "b", 1))
        ego_s = 30.0
        ego_speed = 30.0
        ego_vehicle = self.action_type.vehicle_class(
            road, ego_lane.position(ego_s, 0), speed=ego_speed
        )
        road.vehicles.append(ego_vehicle)
        self.vehicle = ego_vehicle

        other_vehicles_type = utils.class_from_path(self.config["other_vehicles_type"])
        long_jit = float(self.config["spawn_longitude_jitter"])
        speed_jit = float(self.config["spawn_speed_jitter"])
        min_gap = float(self.config["min_spawn_gap"])
        retries = int(self.config["spawn_jitter_retries"])

        # Nominal (lane_id, s, speed) on the pre-merge highway segment ("a","b").
        # Defaults cover 5 NPCs; truncated/extended if highway_vehicles changes.
        nominal_highway = [
            (0, 5.0, 31.5),
            (1, 70.0, 31.0),
            (0, 90.0, 29.0),
            (1, 130.0, 30.5),
            (0, 170.0, 28.5),
        ]
        n_highway = int(self.config["highway_vehicles"])
        while len(nominal_highway) < n_highway:
            lane_id = len(nominal_highway) % 2
            prev_s = nominal_highway[-1][1] if nominal_highway else 0.0
            nominal_highway.append((lane_id, prev_s + 40.0, 30.0))
        nominal_highway = nominal_highway[:n_highway]

        # Track occupied longitudinal centers per lane index (including ego).
        occupied: dict[tuple, list[float]] = {("a", "b", 1): [ego_s]}

        def _fits(lane_index, s: float) -> bool:
            return all(
                abs(s - other) >= min_gap for other in occupied.get(lane_index, [])
            )

        def _spawn(lane_index, s_nom: float, speed_nom: float, s_min: float, s_max: float):
            lane = road.network.get_lane(lane_index)
            for _ in range(retries):
                s = float(np.clip(s_nom + rng.uniform(-long_jit, long_jit), s_min, s_max))
                if not _fits(lane_index, s):
                    continue
                speed = float(max(15.0, speed_nom + rng.uniform(-speed_jit, speed_jit)))
                vehicle = other_vehicles_type(road, lane.position(s, 0), speed=speed)
                road.vehicles.append(vehicle)
                occupied.setdefault(lane_index, []).append(s)
                return vehicle
            # Fallback: nominal pose if jitter keeps colliding.
            s = float(np.clip(s_nom, s_min, s_max))
            vehicle = other_vehicles_type(road, lane.position(s, 0), speed=speed_nom)
            road.vehicles.append(vehicle)
            occupied.setdefault(lane_index, []).append(s)
            return vehicle

        # a->b highway length is 230m (ends[0]+ends[1]).
        highway_s_max = 220.0
        for lane_id, s_nom, speed_nom in nominal_highway:
            _spawn(("a", "b", lane_id), s_nom, speed_nom, s_min=0.0, s_max=highway_s_max)

        # Ramp merger (j->k is 150m long).
        merging_v = _spawn(("j", "k", 0), 110.0, 20.0, s_min=60.0, s_max=140.0)
        merging_v.target_speed = 30


class MergeEnvMEBasic(MergeEnv):
    """
    Merge counterpart of HighwayEnvMEBasic for the first-experiment reward setup:
        - lower simulation frequency
        - collision + high speed + right-lane + constant offset
        - no merging-speed altruism or lane-change cost
        - no [0, 1] lmap (same raw-scale +1 formula as HighwayEnvMEBasic)
    """

    @classmethod
    def default_config(cls) -> dict:
        cfg = super().default_config()
        cfg.update({
            "simulation_frequency": 5,
            "collision_reward": -0.5,
            "right_lane_reward": 0.1,
            "high_speed_reward": 0.4,
            "merging_speed_reward": 0.0,
            "lane_change_reward": 0,
            "reward_speed_range": [20, 30],
        })
        return cfg

    def _reward(self, action: int) -> float:
        """
        Match HighwayEnvMEBasic (no lmap to [0, 1]):
            collision_reward * crashed
            + right_lane_reward * lane_fraction
            + high_speed_reward * clip(lmap(forward_speed, reward_speed_range, [0, 1]), 0, 1)
            + 1
        Zero when off-road. Merging altruism / lane-change terms are excluded.
        """
        del action  # unused; DiscreteMetaAction reward does not depend on action here
        neighbours = self.road.network.all_side_lanes(self.vehicle.lane_index)
        lane = self.vehicle.target_lane_index[2] if isinstance(self.vehicle, ControlledVehicle) \
            else self.vehicle.lane_index[2]
        lane_fraction = lane / max(len(neighbours) - 1, 1)

        forward_speed = self.vehicle.speed * np.cos(self.vehicle.heading)
        scaled_speed = utils.lmap(forward_speed, self.config["reward_speed_range"], [0, 1])
        reward = (
            self.config["collision_reward"] * self.vehicle.crashed
            + self.config["right_lane_reward"] * lane_fraction
            + self.config["high_speed_reward"] * np.clip(scaled_speed, 0, 1)
            + 1
        )
        return 0 if not self.vehicle.on_road else reward


class MergeEnvMEAddCourtesyReward(MergeEnvMEBasic):
    """Residual-train env: courtesy add-on only (``r = -sqrt(x)`` from actual gap).

    Basic collision / speed / right-lane terms are zeroed. Courtesy applies when a
    ramp merger exists, ego is on the target highway lane, and ego is behind or
    in line with the merger (see ``merge_courtesy.courtesy_add_on_reward``).
    """

    @classmethod
    def default_config(cls) -> dict:
        cfg = super().default_config()
        cfg.update({
            "collision_reward": 0.0,
            "right_lane_reward": 0.0,
            "high_speed_reward": 0.0,
            "merging_speed_reward": 0.0,
            "lane_change_reward": 0.0,
            # Envelope length [m] (matches MergeCourtesyNormProfile.COURTESY_DISTANCE).
            "courtesy_distance": 90.0,
            "courtesy_target_lane_id": 1,
        })
        return cfg

    def _reward(self, action: int) -> float:
        del action  # state-based add-on (actual gap), like highway AddRight
        from highway_env.envs.merge_courtesy import courtesy_add_on_reward

        self.added_reward = courtesy_add_on_reward(
            self.vehicle,
            courtesy_distance=float(self.config["courtesy_distance"]),
            target_lane_id=int(self.config["courtesy_target_lane_id"]),
        )
        self.basic_reward = 0.0
        return float(self.added_reward)


def _register(id: str, entry_point: str, **kwargs) -> None:
    """Register with gymnasium (preferred) and gym when available."""
    for register_fn in (register_gymnasium, register_gym):
        if register_fn is None:
            continue
        try:
            register_fn(id=id, entry_point=entry_point, **kwargs)
        except Exception:
            # Already registered in this registry
            pass


_register(
    id='merge-v0',
    entry_point='highway_env.envs:MergeEnv',
)

_register(
    id='merge-ME-basic-v0',
    entry_point='highway_env.envs:MergeEnvMEBasic',
)

_register(
    id='merge-ME-basic-AddCourtesyReward-v0',
    entry_point='highway_env.envs:MergeEnvMEAddCourtesyReward',
)
