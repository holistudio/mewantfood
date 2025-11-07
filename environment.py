class Table (object):
    def __init__(self, r, n_seats, max_spoon_angle=45, include_other_rew=False, max_timesteps=5000):
        self.radius = r
        self.n_seats = n_seats

        agent_offset = 1
        food_offset = 1

        self.agent_locations = []
        self.agent_mouths_open = [False for _ in range(n_seats)]
        self.food_locations = []
        self.food_need_replenish = [False for _ in range(n_seats)]
        
        theta = 0
        theta_inc = 360/n_seats
        
        min_spoon_len = agent_offset + r * 2 - food_offset
        max_spoon_len = min_spoon_len + food_offset + agent_offset

        self.max_spoon_angle = max_spoon_angle
        self.min_spoon_angle = -max_spoon_angle

        self.spoon_lengths = [(min_spoon_len + max_spoon_len)/2 for _ in range(n_seats)]
        self.spoon_thetas = [0 for _ in range(n_seats)]

        self.action_space = {
            "spoon_length": (min_spoon_len, max_spoon_len),
            "spoon_theta": (-max_spoon_angle, max_spoon_angle),
            "open_mouth": (False, True),
            "pick_food": (False, True),
            "drop_food": (False, True) # this is masked from the agent unless they have food on their spoon
        }

        self.rewards = {}

        for n in self.n_seats:
            self.food_locations.append((r - food_offset), theta)
            self.agent_locations.append((r + agent_offset, theta))
            key = f'player_{n}'
            self.rewards[key] = 0
            theta += theta_inc 

        self.state = {
            "agent_locations": self.agent_locations,
            "agent_mouths_open": self.agent_mouths_open,
            "food_locations": self.food_locations,
            "spoon_lengths": self.spoon_lengths,
            "spoon_thetas": self.spoon_thetas,
        }

        self.agent_rewards = [0 for _ in range(n_seats)]
        self.include_other_rew = include_other_rew
        if include_other_rew:
            self.state["agent_rewards"] = self.agent_rewards

        self.terminal = False
        self.t = 0
        self.max_timesteps = max_timesteps
        pass

    def get_observation(self, agent):
        """
        Get the observation space w.r.t. to a specific agent's perspective.
        """
        
        agent_id = int(agent.split('_')[-1])
        looped = False

        # most observations list the agent's state first before the other agents' states
        obs_dict = {
            "agent_locations": [self.state['agent_locations'][agent_id]],
            "agent_mouths_open": [self.state['agent_mouths_open'][agent_id]],
            "food_locations": [self.state['food_locations'][agent_id]],
            "spoon_lengths": [self.state['spoon_lengths'][agent_id]],
            "spoon_thetas": [self.state['spoon_thetas'][agent_id]]
        }

        # for when rewards are provided in the observation
        # ONLY the OTHER agents' rewards are given as part of the observation
        if self.include_other_rew:
            obs_dict["agent_rewards"] = []

        idx = agent_id + 1
        while not looped:
            obs_dict['agent_locations'].append(self.state['agent_locations'][idx])
            obs_dict['agent_mouths_open'].append(self.state['agent_mouths_open'][idx])
            obs_dict['food_locations'].append(self.state['food_locations'][idx])
            obs_dict['spoon_lengths'].append(self.state['spoon_lengths'][idx])
            obs_dict['spoon_thetas'].append(self.state['spoon_thetas'][idx])

            # for when rewards are provided in the observation
            # ONLY the OTHER agents' rewards are given as part of the observation
            if self.include_other_rew:
                obs_dict["agent_rewards"].append(self.state["agent_rewards"][idx])

            idx += 1
            if idx == agent_id:
                looped = True
            if idx >= self.n_seats:
                idx = 0

        return obs_dict
    
    def check_terminal(self):
        if self.t > self.max_timesteps:
            return True
        return False