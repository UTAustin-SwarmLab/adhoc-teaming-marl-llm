# Consists of modifications to the original ForaginEnv to include agent roles
from lbforaging.foraging import ForagingEnv


# Gemini Roles

import random  # You might need other imports as well

# Assuming you have an Action enum defined 
class Action(Enum):
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


class RiskTaker:
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

    def _find_high_value_target(self, observation, player_obs):
        neighbors = neighbors_within_sight(observation, player_obs.position)
        best_target = None
        best_potential = player_obs.level

        for x, y in neighbors[0]:
            food_level = observation.field[x, y]

            if food_level > player_obs.level:  
                collective_level = player_obs.level
                for nearby_player in neighbors[1]:
                    if self._can_reach(nearby_player, (x, y), observation): 
                        collective_level += nearby_player.level

                if collective_level >= food_level and collective_level > best_potential:
                    best_target = (x, y)
                    best_potential = collective_level

        return best_target

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
        return distance <= player_obs.sight  

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

    def _find_promising_target(self, observation, player_obs):
        # Prioritize targets like RiskTaker, but additionally check:
        targets = [target for target in self._find_high_value_target(observation, player_obs)]  # Targets from RiskTaker logic

        for x, y in targets:
            # Filter where collection hasn't fully started:
            adjacent_agents = [p for p in observation.players if abs(p.position[0] - x) <= 1 and abs(p.position[1] - y) <= 1]
            if len(adjacent_agents) <= 2:  # Example threshold, indicating collection not fully underway
                return (x, y)  

        # Fallback to RiskTaker logic if no promising target found
        return self._find_high_value_target(observation, player_obs)   
    
class ReactiveHelper:
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles = {
            "prospector": Prospector(),
            "opportunist": Opportunist(),
            "strategic_coordinator": StrategicCoordinator(),
            "load_balancer": LoadBalancer()
        }

    def step(self, action_dict):
        actions = {}
        for agent_id, player_obs in self.players.items():
            role = player_obs.role
            actions[agent_id] = self.roles[role]._step(player_obs, action_dict)
        return super().step(actions)

    def reset(self):
        obs = super().reset()
        for agent_id, player_obs in self.players.items():
            player_obs.role = random.choice(list(self.roles.keys()))
        return obs
    
    