# Consists of modifications to the original ForaginEnv to include agent roles



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


# These roles are obtained from Gemini Advanced
class Prospector:
    def __init__(self):
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

class Opportunist:
    def __init__(self):
        pass

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:    
                # Check for immediately available food
                for action in [Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST]:
                    new_pos = self._get_new_position(player_obs.position, action)
                    if observation.field[new_pos[0], new_pos[1]] >= player_obs.level:
                        return Action.LOAD

                # Prioritize collecting food if possible
                if observation.field[player_obs.position[0], player_obs.position[1]] >= player_obs.level:
                    return Action.LOAD

                # Move towards food (similar to your greedy example)
                min_dist = float('inf')
                target_food = None
                for x in range(observation.field.shape[0]):
                    for y in range(observation.field.shape[1]):
                        if observation.field[x, y] > 0:
                            dist = abs(x - player_obs.position[0]) + abs(y - player_obs.position[1])
                            if dist < min_dist:
                                min_dist = dist
                                target_food = (x, y)
                if target_food:
                    return self._move_towards(player_obs.position, target_food) 

        return Action.NONE 

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

class StrategicCoordinator:
    def __init__(self):
        self.potential_targets = {}

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                self._update_potential_targets(observation) 
                best_target = self._select_best_target()
                if best_target:
                    return self._move_towards(player_obs.position, best_target) 
        return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])

    def _update_potential_targets(self, observation): 
        for x in range(observation.field.shape[0]):
            for y in range(observation.field.shape[1]):
                if (x, y) not in self.potential_targets and observation.field[x, y] > 0:
                    neighbor_levels = self._get_neighboring_agent_levels(observation, x, y)
                    if sum(neighbor_levels) + player_obs.level >= observation.field[x, y]:
                        self.potential_targets[(x, y)] = neighbor_levels  
 
    def _get_neighboring_agent_levels(self, observation, x, y):
        neighbor_levels = []
        for player_obs in observation.players:
           dist = abs(player_obs.position[0] - x) + abs(player_obs.position[1] - y)
           if dist <= 1:  # Check immediate neighbors
               neighbor_levels.append(player_obs.level)
        return neighbor_levels 

    def _select_best_target(self):
        best_target = None
        max_potential = 0
        for (loc, food_level), agent_levels in self.potential_targets.items():
            total_level = player_obs.level + sum(agent_levels)
            if total_level >= food_level and total_level > max_potential:
                best_target = loc
                max_potential = total_level
        return best_target

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

    
class LoadBalancer:
    def __init__(self):
        self.partial_targets = {}  # (Location, Food Level): [Agent levels on site] 

    def _step(self, observation):
        for player_obs in observation.players:
            if player_obs.is_self:
                self._update_partial_targets(observation) 
                best_target = self._select_best_target()
                if best_target:
                    return self._move_towards(player_obs.position, best_target) 
        return random.choice([Action.NORTH, Action.SOUTH, Action.WEST, Action.EAST])
    
    def _update_potential_targets(self, player_obs, observation): 
        for x in range(observation.field.shape[0]):
            for y in range(observation.field.shape[1]):
                if (x, y) not in self.potential_targets and observation.field[x, y] > 0:
                    neighbor_levels = self._get_neighboring_agent_levels(observation, x, y)
                    if sum(neighbor_levels) + player_obs.level >= observation.field[x, y]:
                        self.potential_targets[(x, y)] = neighbor_levels  

    def _get_neighboring_agent_levels(self, observation, x, y):
        neighbor_levels = []
        for player_obs in observation.players:
            if player_obs.is_self:
                continue  # Skip the current agent itself
            dist = abs(player_obs.position[0] - x) + abs(player_obs.position[1] - y)
            if dist <= 1:  # Check immediate neighbors
                neighbor_levels.append(player_obs.level)
        return neighbor_levels 

    def _select_best_target(self, player_obs):  # Modified for better decision-making
        best_target = None
        max_potential = 0
        for (loc, food_level), agent_levels in self.potential_targets.items():
            total_level = player_obs.level + sum(agent_levels)
            if total_level >= food_level and total_level > max_potential:
                # Prioritize closer targets (add tie-breaking logic)
                dist = abs(player_obs.position[0] - loc[0]) + abs(player_obs.position[1] - loc[1])
                if best_target is None or dist < best_dist:
                    best_target = loc
                    max_potential = total_level
                    best_dist = dist
        return best_target

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