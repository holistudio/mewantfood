class Table (object):
    def __init__(self, r, n_seats, max_spoon_angle=45, include_other_rew=False):
        self.radius = r
        self.n_seats = n_seats

        agent_offset = 1
        food_offset = 1

        self.agent_locations = []
        self.food_locations = []
        self.food_need_replenish = [False for _ in range(n_seats)]
        
        theta = 0
        theta_inc = 360/n_seats
        
        min_spoon_len = agent_offset + r * 2 - food_offset
        max_spoon_len = min_spoon_len + food_offset + agent_offset

        self.max_spoon_angle = max_spoon_angle
        self.min_spoon_angle = -max_spoon_angle

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
            "agent_mouths_open": [False for _ in range(n_seats)],
            "food_locations": self.food_locations,
            "spoon_lengths": [(min_spoon_len + max_spoon_len)/2 for _ in range(n_seats)],
            "spoon_thetas": [0 for _ in range(n_seats)],
        }

        if include_other_rew:
            self.state["agent_rewards"] = [0 for _ in range(n_seats)]
        pass