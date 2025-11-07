class Food(object):
    def __init__(self, id, r, theta):
        self.id = id
        self.location = (r, theta)
        self._initial_loc = (r, theta)
        pass

    def reset(self):
        self.location = self._initial_loc
        pass

class Spoon(object):
    def __init__(self, id, length, theta, agent_id=-1):
        self.id = id
        self.length = length
        self.theta = theta

        self.agent_id = agent_id
        
        self.has_food = False
        self.food_id = -1
        pass

    def pick_up(self, food_id):
        self.has_food = True
        self.food_id = food_id
        pass

    def drop(self):
        self.has_food = False
        self.food_id = -1
        pass

class Player(object):
    def __init__(self, id, r, theta, spoon_id=-1, full_time_limit=10):
        self.id = id
        self.location = (r, theta)
        self.mouth_open = False
        self.spoon_id = spoon_id
        self.hungry = True
        self.hunger = 0
        self.full_timer = -1
        self.full_time_limit = full_time_limit
        pass

    def step(self):
        """
        Player hunger changes at each step depending on 
        if it is hungry and how long it has been full
        """
        if self.hungry:
            self.hunger -= 0.1
        else:
            if self.full_timer > self.full_time_limit:
                self.full_timer -= 1
            else:
                self.hungry = True
        pass

class Environment(object):
    def __init__(self, r, n_seats, max_spoon_angle=45, feed_dist= 0.1, include_other_rew=False, max_timesteps=5000):
        self.radius = r
        self.n_seats = n_seats

        player_offset = 1
        food_offset = 1

        self.players = {}
        self.spoons = {}
        self.foods = {}

        theta = 0
        theta_inc = 360/n_seats

        min_spoon_len = player_offset + r * 2 - food_offset
        max_spoon_len = min_spoon_len + food_offset + player_offset

        self.max_spoon_angle = max_spoon_angle
        self.min_spoon_angle = -max_spoon_angle

        for i in range(n_seats):
            self.foods[i] = Food(id=i, r=r - food_offset, theta=theta)
            self.players[f"player_{i}"] = Player(id=i, r=r + player_offset, theta=theta, spoon_id=i)
            self.spoons[i] = Spoon(id=i, length=(min_spoon_len + max_spoon_len)/2, theta=0, agent_id=i)
            theta += theta_inc



        

        self.feed_dist = feed_dist

        self.action_space = {
            "spoon_length": (min_spoon_len, max_spoon_len),
            "spoon_theta": (-max_spoon_angle, max_spoon_angle),
            "open_mouth": (False, True),
            "pick_food": (False, True),
            "drop_food": (False, True) # this is masked from the player unless they have food on their spoon
        }

        self.player_rewards = [0 for _ in range(n_seats)]
        self.include_other_rew = include_other_rew
        if include_other_rew:
            self.state["player_rewards"] = self.player_rewards

        self.terminal = False
        self.t = 0
        self.max_timesteps = max_timesteps
        pass

    def player_locations(self):
        return [self.players[f"player_{i}"].location for i in range(self.n_seats)]
    
    def player_mouths_open(self):
        return [self.players[f"player_{i}"].mouth_open for i in range(self.n_seats)]
    
    def food_locations(self):
        return [self.foods[i].location for i in range(self.n_seats)]
    
    def spoon_lengths(self):
        return [self.spoons[i].length for i in range(self.n_seats)]
    
    def spoon_thetas(self):
        return [self.spoons[i].theta for i in range(self.n_seats)]
    
    def state(self):
        state_dict = {
            "player_locations": self.player_locations(),
            "player_mouths_open": self.player_mouths_open(),
            "food_locations": self.food_locations(),
            "spoon_lengths": self.spoon_lengths(),
            "spoon_thetas": self.spoon_thetas(),
        }
        return state_dict
    
    def rewards(self):
        rew_dict = {}
        for i in range(self.n_seats):
            key = f"player_{i}"
            rew_dict[key] = self.players[key].hunger
        return rew_dict

    def get_observation(self, player):
        """
        Get the observation space w.r.t. to a specific player's perspective.
        """
        
        player_id = int(player.split('_')[-1])
        looped = False

        # most observations list the player's state first before the other players' states
        obs_dict = {
            "player_locations": [self.state['player_locations'][player_id]],
            "player_mouths_open": [self.state['player_mouths_open'][player_id]],
            "food_locations": [self.state['food_locations'][player_id]],
            "spoon_lengths": [self.state['spoon_lengths'][player_id]],
            "spoon_thetas": [self.state['spoon_thetas'][player_id]]
        }

        # for when rewards are provided in the observation
        # ONLY the OTHER players' rewards are given as part of the observation
        if self.include_other_rew:
            obs_dict["player_rewards"] = []

        idx = player_id + 1
        while not looped:
            obs_dict['player_locations'].append(self.state['player_locations'][idx])
            obs_dict['player_mouths_open'].append(self.state['player_mouths_open'][idx])
            obs_dict['food_locations'].append(self.state['food_locations'][idx])
            obs_dict['spoon_lengths'].append(self.state['spoon_lengths'][idx])
            obs_dict['spoon_thetas'].append(self.state['spoon_thetas'][idx])

            # for when rewards are provided in the observation
            # ONLY the OTHER players' rewards are given as part of the observation
            if self.include_other_rew:
                obs_dict["player_rewards"].append(self.state["player_rewards"][idx])

            idx += 1
            if idx == player_id:
                looped = True
            if idx >= self.n_seats:
                idx = 0

        return obs_dict
    
    def check_terminal(self):
        if self.t > self.max_timesteps:
            return True
        return False
    
    def check_fed(self):
        # get all spoon head locations that have food
        # get locations of all players with open mouth
        # compare distance between all spoon heads with food and open mouth players
        # are within the feed distance
        # return which players are fed and which s
        pass