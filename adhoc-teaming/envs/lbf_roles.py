# Consists of modifications to the original ForaginEnv to include agent roles
from lbforaging.foraging import ForagingEnv
import gym
from enum import IntEnum
# Gemini Roles
import time
import random  # You might need other imports as well
import numpy as np
from ray.rllib.env.multi_agent_env import MultiAgentEnv
from gym.spaces import Dict as GymDict, Discrete, Box
# Assuming you have an Action enum defined 
class Action(IntEnum):
    NONE = 0
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4
    LOAD = 5

class AgentRoles:
    def __init__(self):
        pass

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                # Your role-specific logic here
                return Action.NONE  # Replace with your own action
        return Action.NONE  # Replace with your own action
    
    def _get_new_position(self, current_position, action):
        new_x, new_y = current_position
        if action == Action.NORTH:
            new_x -= 1
        elif action == Action.SOUTH:
            new_x += 1
        elif action == Action.WEST:
            new_y -= 1
        elif action == Action.EAST:
            new_y += 1
        return new_x, new_y

    def _move_towards(self, current_pos, target):
        target_x, target_y = target
        if target_x < current_pos[0]:
            return Action.SOUTH
        elif target_x > current_pos[0]:
            return Action.NORTH
        elif target_y < current_pos[1]:
            return Action.WEST
        elif target_y > current_pos[1]:
            return Action.EAST

# # These roles are obtained from Gemini Advanced
# class Prospector(AgentRoles):
#     def __init__(self):
#         super().__init__()
#         self.last_food_location = None

#     def _step(self, observation):
#         for player_obs in observation.players:
#             if player_obs.is_self:
#                 # Prioritize Exploration:
#                 if random.random() < 0.7:  # 70% chance to explore 
#                     return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])

#                 # Targeted Movement Towards Unexplored Areas:
#                 if self.last_food_location:
#                     x_diff = self.last_food_location[0] - player_obs.position[0]
#                     y_diff = self.last_food_location[1] - player_obs.position[1]
#                     if abs(x_diff) > abs(y_diff):
#                         return Action.NORTH if x_diff < 0 else Action.SOUTH
#                     else:
#                         return Action.WEST if y_diff < 0 else Action.EAST

#                 # Food Discovery:
#                 if observation.field[player_obs.position[0], player_obs.position[1]] > 0:
#                     self.last_food_location = player_obs.position
#                     return Action.LOAD  

#         return Action.NONE  

# class Opportunist(AgentRoles):
#     def __init__(self):
#         pass

#     def _step(self, observation):
#         for player_obs in observation.players:
#             if player_obs.is_self:    
#                 # Check for immediately available food
#                 for action in [Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST]:
#                     new_pos = self._get_new_position(player_obs.position, action)
#                     if observation.field[new_pos[0], new_pos[1]] >= player_obs.level:
#                         return Action.LOAD

#                 # Prioritize collecting food if possible
#                 if observation.field[player_obs.position[0], player_obs.position[1]] >= player_obs.level:
#                     return Action.LOAD

#                 # Move towards food (similar to your greedy example)
#                 min_dist = float('inf')
#                 target_food = None
#                 for x in range(observation.field.shape[0]):
#                     for y in range(observation.field.shape[1]):
#                         if observation.field[x, y] > 0:
#                             dist = abs(x - player_obs.position[0]) + abs(y - player_obs.position[1])
#                             if dist < min_dist:
#                                 min_dist = dist
#                                 target_food = (x, y)
#                 if target_food:
#                     return self._move_towards(player_obs.position, target_food) 

#         return Action.NONE 


# class StrategicCoordinator(AgentRoles):
#     def __init__(self):
#         self.potential_targets = {}

#     def _step(self, observation):
#         for player_obs in observation.players:
#             if player_obs.is_self:
#                 self._update_potential_targets(observation, player_obs) 
#                 best_target = self._select_best_target()
#                 if best_target:
#                     return self._move_towards(player_obs.position, best_target) 
#         return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])

#     def _update_potential_targets(self, observation, player_obs): 
#         for x in range(observation.field.shape[0]):
#             for y in range(observation.field.shape[1]):
#                 if (x, y) not in self.potential_targets and observation.field[x, y] > 0:
#                     neighbor_levels = self._get_neighboring_agent_levels(observation, x, y)
#                     if sum(neighbor_levels) + player_obs.level >= observation.field[x, y]:
#                         self.potential_targets[(x, y)] = neighbor_levels  

#     def _get_neighboring_agent_levels(self, observation, x, y):
#         neighbor_levels = []
#         for player_obs in observation.players:
#             if player_obs.is_self:
#                 continue  # Skip the current agent itself
#             dist = abs(player_obs.position[0] - x) + abs(player_obs.position[1] - y)
#             if dist <= 1:  # Check immediate neighbors
#                 neighbor_levels.append(player_obs.level)
#         return neighbor_levels 

#     def _select_best_target(self, player_obs):  # Modified for better decision-making
#         best_target = None
#         max_potential = 0
#         for (loc, food_level), agent_levels in self.potential_targets.items():
#             total_level = player_obs.level + sum(agent_levels)
#             if total_level >= food_level and total_level > max_potential:
#                 # Prioritize closer targets (add tie-breaking logic)
#                 dist = abs(player_obs.position[0] - loc[0]) + abs(player_obs.position[1] - loc[1])
#                 if best_target is None or dist < best_dist:
#                     best_target = loc
#                     max_potential = total_level
#                     best_dist = dist
#         return best_target

# class LoadBalancer(AgentRoles):
#     def __init__(self):
#         self.partial_targets = {}  # (Location, Food Level): [Agent levels on site] 

#     def _step(self, observation):
#         for player_obs in observation.players:
#             if player_obs.is_self:
#                 self._update_partial_targets(observation) 
#                 best_target = self._select_best_target(player_obs)
#                 if best_target:
#                     return self._move_towards(player_obs.position, best_target) 
#         return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])

#     def _update_partial_targets(self, observation): 
#         for x in range(observation.field.shape[0]):
#             for y in range(observation.field.shape[1]):
#                 if (x, y) in self.partial_targets:
#                     # If target collected, remove it
#                     if observation.field[x, y] == 0:
#                         del self.partial_targets[(x, y)]
#                     else: 
#                         # Update agent levels present if changes observed
#                         self.partial_targets[(x, y)] = self._get_neighboring_agent_levels(observation, x, y)
#                 elif observation.field[x, y] > 0:
#                     # Add partially collected food as a potential target
#                     neighbor_levels = self._get_neighboring_agent_levels(observation, x, y)
#                     self.partial_targets[(x, y)] = neighbor_levels  

#     def _get_neighboring_agent_levels(self, observation, x, y):
#         neighbor_levels = []
#         for player_obs in observation.players:
#             if player_obs.is_self:
#                 continue  # Skip the current agent itself
#             dist = abs(player_obs.position[0] - x) + abs(player_obs.position[1] - y)
#             if dist <= 1:  # Check immediate neighbors
#                 neighbor_levels.append(player_obs.level)
#         return neighbor_levels 
    
#     def _select_best_target(self,player_obs):
#         best_target = None
#         min_remaining = float('inf')
#         for (loc, food_level), agent_levels in self.partial_targets.items():
#             remaining_level = food_level - sum(agent_levels) 
#             if 0 < remaining_level <= player_obs.level and remaining_level < min_remaining: 
#                 best_target = loc
#                 min_remaining = remaining_level
#         return best_target



def neighbors_within_sight(observation, position):  
    """ Helper to extract visible food and other agents around a position """
    food_neighbors = []
    agent_neighbors = []
    sight = observation.sight

    # Assuming sight defines radius around agent
    for x in range(max(0, position[0] - sight), min(observation.field.shape[0], position[0] + sight + 1)):
        for y in range(max(0, position[1] - sight), min(observation.field.shape[1], position[1] + sight + 1)):
            if observation.field[x, y] > 0:
                food_neighbors.append((x, y))
            else:
                for player_obs in observation.players:
                    if (player_obs.position[0] == x and player_obs.position[1] == y):
                        agent_neighbors.append(player_obs)

    return food_neighbors, agent_neighbors


class Prospector(AgentRoles):
    def __init__(self):
        super().__init__()
        self.last_food_location = None

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                # Prioritize Exploration:
                if random.random() < 0.7:  # 70% chance to explore 
                    return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])

                # Targeted Movement Towards Unexplored Areas:
                if self.last_food_location:
                    x_diff = self.last_food_location[0] - player_obs.position[0]
                    y_diff = self.last_food_location[1] - player_obs.position[1]
                    if abs(x_diff) > abs(y_diff):
                        return Action.NORTH if x_diff < 0 else Action.SOUTH
                    else:
                        return Action.WEST if y_diff < 0 else Action.EAST

                # Food Discovery:
                if observation.field[player_obs.position[0], player_obs.position[1]] > 0:
                    self.last_food_location = player_obs.position
                    return Action.LOAD  

        return Action.NONE  

class Opportunist(AgentRoles):
    def __init__(self):
        pass

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                # 1. Immediate collection opportunity?
                for action in [Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST]:
                    new_x = player_obs.position[0] + (action == Action.SOUTH) - (action == Action.NORTH)
                    new_y = player_obs.position[1] + (action == Action.EAST) - (action == Action.WEST)
                    
                    if new_x >= 0 and new_x < observation.field.shape[0] and new_y >= 0 and new_y < observation.field.shape[1]:
                        if observation.field[new_x, new_y] >= player_obs.level:
                            return Action.LOAD

                # 2. If not, move towards nearest visible food
                nearest_food = self._find_nearest_food(observation, player_obs)
                if nearest_food:
                    return self._move_towards(player_obs.position, nearest_food)

        return Action.NONE  # Default if no opportunities found

    def _find_nearest_food(self, observation, player_obs):
        neighbors = neighbors_within_sight(observation, player_obs.position)
        min_dist = float('inf')
        nearest_food = None

        for x, y in neighbors[0]:  # Check visible food 
            if observation.field[x, y] >= player_obs.level:
                dist = abs(x - player_obs.position[0]) + abs(y - player_obs.position[1])
                if dist < min_dist:
                    min_dist = dist
                    nearest_food = (x, y)

        return nearest_food


class RiskTaker(AgentRoles):
    def __init__(self):
        self.target = None
        self.wait_steps = 0  

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:            
                if not self.target:
                    self.target = self._find_high_value_target(observation, player_obs)

                if self.target:
                    action = self._move_towards(player_obs.position, self.target)
                    self.wait_steps += 1

                    # Check if help has arrived or timeout
                    if self._can_load(observation) or self.wait_steps > 5:  
                        self.target = None 
                        self.wait_steps = 0
                        return Action.LOAD
                    else:
                        return action  

        return Action.NONE  

    # def _find_high_value_target(self, observation, player_obs):
    #     neighbors = neighbors_within_sight(observation, player_obs.position)
    #     best_target = None
    #     best_potential = player_obs.level

    #     for x, y in neighbors[0]:
    #         food_level = observation.field[x, y]

    #         if food_level > player_obs.level:  
    #             collective_level = player_obs.level
    #             for nearby_player in neighbors[1]:
    #                 if self._can_reach(nearby_player, (x, y), observation): 
    #                     collective_level += nearby_player.level

    #             if collective_level >= food_level and collective_level > best_potential:
    #                 best_target = (x, y)
    #                 best_potential = collective_level

    #     return best_target
    
    def _find_high_value_target(self, observation, player_obs):
        neighbors = neighbors_within_sight(observation, player_obs.position)
        best_target = None
        best_potential = player_obs.level

        for x, y in neighbors[0]:  
            food_level = observation.field[x, y]

            if food_level > player_obs.level:  
                collective_level = player_obs.level
                for nearby_player in neighbors[1]:
                    if self._can_estimate_reach(nearby_player, (x, y), observation): 
                        collective_level += nearby_player.level

                if collective_level >= food_level and collective_level > best_potential:
                    best_target = (x, y)
                    best_potential = collective_level

        return best_target  

    def _can_estimate_reach(self, player_obs, target, observation):
        # Replace with your logic: Consider obstacles, more accurate reachability
        distance = abs(player_obs.position[0] - target[0]) + abs(player_obs.position[1] - target[1])
        return distance <= observation.sight * 1.5  # Placeholder
    
    def _can_load(self, observation):
        food_x, food_y = self.target
        neighbors = neighbors_within_sight(observation, self.target)

        total_level = 0
        for player_obs in neighbors[1]: 
            total_level += player_obs.level

        return total_level >= observation.field[food_x, food_y]

    def _can_reach(self, player_obs, target, observation):
        # Simple reachability 
        distance = abs(player_obs.position[0] - target[0]) + abs(player_obs.position[1] - target[1])
        return distance <= observation.sight  

class StrategicScout(RiskTaker): 
    def __init__(self):
        super().__init__()
        self.target = None
        self.wait_steps = 0  

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:            
                if not self.target:
                    self.target = self._find_promising_target(observation, player_obs)

                if self.target:
                    action = self._move_towards(player_obs.position, self.target)
                    self.wait_steps += 1

                    # Check if help has arrived or timeout
                    if self._can_load(observation) or self.wait_steps > 5:  
                        self.target = None 
                        self.wait_steps = 0
                        return Action.LOAD
                    else:
                        return action  

        return Action.NONE  

    # def _find_promising_target(self, observation, player_obs):
    #     # Prioritize targets like RiskTaker, but additionally check:
    #     targets = [target for target in self._find_high_value_target(observation, player_obs)]  # Targets from RiskTaker logic

    #     for x, y in targets:
    #         # Filter where collection hasn't fully started:
    #         adjacent_agents = [p for p in observation.players if abs(p.position[0] - x) <= 1 and abs(p.position[1] - y) <= 1]
    #         if len(adjacent_agents) <= 2:  # Example threshold, indicating collection not fully underway
    #             return (x, y)  

    #     # Fallback to RiskTaker logic if no promising target found
    #     return self._find_high_value_target(observation, player_obs)   
    
    def _find_promising_target(self, observation, player_obs):
        # Prioritize targets like RiskTaker, but additionally check:
        targets = [self._find_high_value_target(observation, player_obs)]
        
        if targets == [None]:
            return None 

        for x, y in targets:
            # Filter where collection hasn't fully started:
            adjacent_agents = [p for p in observation.players if abs(p.position[0] - x) <= 1 and abs(p.position[1] - y) <= 1]
            if len(adjacent_agents) <= 2:
                return (x, y)  

        # Fallback to RiskTaker logic if no promising target found
        return self._find_high_value_target(observation, player_obs) 
    
class ReactiveHelper(AgentRoles):
    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                neighbors = neighbors_within_sight(observation, player_obs.position)
                collection_target = self._find_collection_target(observation, neighbors)  # New helper function

                if collection_target:
                    if self._can_load_at_target(observation, collection_target):
                        return Action.LOAD
                    else:
                        return self._move_towards(player_obs.position, collection_target)
                

        return Action.NONE 

    def _find_collection_target(self, observation, neighbors):
        for x, y in neighbors[0]:  # Check for adjacent food
            adjacent_agents = [p for p in observation.players if abs(p.position[0] - x) <= 1 and abs(p.position[1] - y) <= 1]
            if len(adjacent_agents) > 1 and observation.field[x, y] > adjacent_agents[0].level:
            # Collection seems underway (multiple agents, food exceeds level of one)
                return (x, y)
        return None 

    def _can_load_at_target(self, observation, target):
        food_x, food_y = target
        neighbors = neighbors_within_sight(observation, target)

        total_level = 0
        for player_obs in neighbors[1]: 
            total_level += player_obs.level

        return total_level >= observation.field[food_x, food_y]

class LBFRoles(ForagingEnv):
    def __init__(self, config):
        super().__init__(**config)
        self.roles = {
            "prospector": Prospector(),
            "opportunist": Opportunist(),
            "strategic_scout": StrategicScout(),
            "reactive_helper": ReactiveHelper(),
            "risk_taker": RiskTaker()
        }
        self.role_keys = list(self.roles.keys())
        self.action_space = gym.spaces.Tuple(tuple([gym.spaces.Discrete(5)] * len(self.players)))

    def step(self, action_dict):
        actions = []
        for player, (agent_id, action_role) in zip(self.players,action_dict.items()):
            player_obs = self._make_obs(player)
            player_role = self.roles[self.role_keys[action_role]]
            actions.append(int(player_role._step(player_obs)))
        return super().step(actions)

    def reset(self):
        obs = super().reset()
        return obs


policy_mapping_dict = {
    "all_scenario": {
        "description": "lbf all scenarios",
        "team_prefix": ("agent_",),
        "all_agents_one_policy": True,
        "one_agent_one_policy": True,
    },
} 
class RLlibLBFRoles(MultiAgentEnv):

    def __init__(self, env_config):
        map_name = env_config["map_name"]
        env_config.pop("map_name", None)
        field_size_y = env_config.pop("field_size_y", None)
        field_size_x = env_config.pop("field_size_x", None)

        env_config["field_size"] = (field_size_y, field_size_x)
        self.env = LBFRoles(**env_config)

        self.action_space = self.env.action_space[0]
        self.observation_space = GymDict({"obs": Box(
            low=-100.0,
            high=100.0,
            shape=(self.env.observation_space[0].shape[0],),
            dtype=self.env.observation_space[0].dtype)})
        self.num_agents = self.env.n_agents
        self.agents = ["agent_{}".format(i) for i in range(self.num_agents)]
        env_config["field_size_y"] = field_size_y
        env_config["field_size_x"] = field_size_x
        env_config["map_name"] = map_name
        self.env_config = env_config

    def reset(self):
        original_obs = self.env.reset()
        obs = {}
        for x in range(self.num_agents):
            obs["agent_%d" % x] = {
                "obs": original_obs[x]
            }
        return obs

    def step(self, action_dict):
        actions = []
        for key, value in sorted(action_dict.items()):
            actions.append(value)
        o, r, d, i = self.env.step(tuple(actions))
        rewards = {}
        obs = {}
        infos = {}
        done_flag = False
        for pos, key in enumerate(sorted(action_dict.keys())):
            infos[key] = i
            rewards[key] = r[pos]
            obs[key] = {
                "obs": o[pos]
            }
            done_flag = d[pos] or done_flag
        dones = {"__all__": done_flag}
        return obs, rewards, dones, infos

    def get_env_info(self):
        env_info = {
            "space_obs": self.observation_space,
            "space_act": self.action_space,
            "num_agents": self.num_agents,
            "episode_limit": self.env_config["max_episode_steps"],
            "policy_mapping_info": policy_mapping_dict
        }
        return env_info

    def close(self):
        self.env.close()


if __name__=="__main__":
    config_dict = {
        'players' : 10,
        'field_size' : [20,20],
        'max_food' : 30,
        'sight' : 5,
        'force_coop' : False,
        'max_episode_steps' : 100,
        'max_player_level' : 10
    }
    env = LBFRoles(config=config_dict)
    obs = env.reset()
    env.render()
    time.sleep(0.5)
    done = False
    while not done:
        action_dict = {agent_id: random.choice(list(range(len(env.roles.keys())))) for agent_id in env.players}
        obs, reward, done, info = env.step(action_dict)
        env.render(mode='human')
        done = np.all(done)
    env.close()