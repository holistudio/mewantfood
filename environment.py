import math

def polar_to_cartesian(r, theta):
    # assume theta is in degrees
    theta = theta * math.pi / 180
    return r*math.cos(theta), r*math.sin(theta)

def distance(p1, p2):
    p1x, p1y = p1
    p2x, p2y = p2
    return math.sqrt((p1x - p2x)**2 + (p1y - p2y)**2)

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
    def __init__(self, id, length, theta, player_id=-1):
        self.id = id
        self.length = length
        self.theta = theta

        self.player_id = player_id
        
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
            self.spoons[i] = Spoon(id=i, length=(min_spoon_len + max_spoon_len)/2, theta=0, player_id=i)
            theta += theta_inc

        self.feed_dist = feed_dist

        self.action_space = {
            "spoon_length": (min_spoon_len, max_spoon_len),
            "spoon_theta": (-max_spoon_angle, max_spoon_angle),
            "open_mouth": (False, True),
            "pick_food": (False, True),
            "drop_food": (False, True) # this is masked from the player unless they have food on their spoon
        }

        self.include_other_rew = include_other_rew

        self.terminal = False
        self.t = 0
        self.max_timesteps = max_timesteps

        self.player_ptr = 0
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
    
    def observation(self, player):
        """
        Get the observation space w.r.t. to a specific player's perspective.
        """
        
        player_id = int(player.split('_')[-1])
        
        # most observations list the player's state first before the other players' states
        obs_dict = {
            "player_locations": [self.state()['player_locations'][player_id]],
            "player_mouths_open": [self.state()['player_mouths_open'][player_id]],
            "food_locations": [self.state()['food_locations'][player_id]],
            "spoon_lengths": [self.state()['spoon_lengths'][player_id]],
            "spoon_thetas": [self.state()['spoon_thetas'][player_id]]
        }

        # for when rewards are provided in the observation
        # ONLY the OTHER players' rewards are given as part of the observation
        if self.include_other_rew:
            obs_dict["player_rewards"] = []

        idx = player_id + 1
        looped = False
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
    
    def rewards(self):
        rew_dict = {}
        for i in range(self.n_seats):
            key = f"player_{i}"
            rew_dict[key] = self.players[key].hunger
        return rew_dict
    
    def check_terminal(self):
        if self.t > self.max_timesteps:
            return True
        return False
    
    def check_fed(self):
        # get all spoon head locations that have food
        spoons_w_food = [self.spoons[i] for i in range(self.n_seats) if self.spoons[i].has_food]
        players_w_food = [self.players[f"player_{s.player_id}"] for s in spoons_w_food]
        
        spoon_heads_w_food = []
        for i,s in enumerate(spoons_w_food):
            pr, ptheta = players_w_food[i].location
            sr, stheta = s.length, s.theta
            px, py = polar_to_cartesian(pr, ptheta)

            sx, sy = polar_to_cartesian(sr, stheta)
            sx, sy = sx+px, sy+py
            spoon_heads_w_food.append((sx,sy))
        
        # get locations of all players with open mouth
        players_open = [self.players[f"player_{i}"] for i in range(self.n_seats) if self.players[f"player_{i}"].mouth_open]
        players_open_locs = []
        for p in players_open:
            pr, ptheta = p.location
            px, py = polar_to_cartesian(pr, ptheta)
            players_open_locs.append((px, py))

        players_fed = []
        spoons_fed = []
        # compare distance between all spoon heads with food and open mouth players
        # are within the feed distance
        for i in range(len(spoon_heads_w_food)):
            sx, sy = spoon_heads_w_food[i]
            for j in range(len(players_open_locs)):
                px, py = players_open_locs
                if distance((sx, sy),(px, py)) <= self.feed_dist:
                    spoons_fed.append(spoons_w_food[i].id)
                    players_fed.append(players_open[j].id)
        
        # return which players are fed and which spoons are fed and should be empty
        return players_fed, spoons_fed
    
    def release_food(self, player_id, spoon_id):
        spoon = self.spoons[spoon_id]
        food = self.foods[spoon.food_id]

        spoon.drop()
        food.reset()
        
        player = self.players[player_id]
        player.hunger += 1
        pass

    def check_pickup(self, spoon_id):
        """
        checks if spoon can pick up any food
        """
        spoon = self.spoons[spoon_id]
        sr, stheta = spoon.length, spoon.theta
        sx, sy = spoon.location(sr, stheta)

        player = self.players[spoon.player_id]
        pr, ptheta = player.location
        px, py = polar_to_cartesian(pr, ptheta)

        sx, sy = sx+px, sy+py

        foods_picked = -1
        for food_id in self.foods.keys():
            food = self.foods[food_id]
            fr, ftheta = food.location
            fx, fy = polar_to_cartesian(fr, ftheta)
            if distance((sx,sy), (fx,fy)) <= self.feed_dist:
                foods_picked = food_id
                break
        return foods_picked
    
    def pickup_food(self, spoon_id, food_id):
        spoon = self.spoons[spoon_id]
        spoon.pick_up(food_id)

        food = self.foods[food_id]
        food.location = (-1, -1)

    def iter(self):
        if self.player_ptr >= self.n_seats:
            self.player_ptr = 0
        else:
            self.player_ptr += 1