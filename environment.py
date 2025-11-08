import math
import random
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
            obs_dict['player_locations'].append(self.state()['player_locations'][idx])
            obs_dict['player_mouths_open'].append(self.state()['player_mouths_open'][idx])
            obs_dict['food_locations'].append(self.state()['food_locations'][idx])
            obs_dict['spoon_lengths'].append(self.state()['spoon_lengths'][idx])
            obs_dict['spoon_thetas'].append(self.state()['spoon_thetas'][idx])

            # for when rewards are provided in the observation
            # ONLY the OTHER players' rewards are given as part of the observation
            if self.include_other_rew:
                obs_dict["player_rewards"].append(self.state()["player_rewards"][idx])

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
    
    def check_feed_range(self, spoon_id):
        """
        checks if spoon can release food into a player's open mouth
        assume spoon already has food and player has already decided to release food
        """
        spoon = self.spoons[spoon_id]
        assert spoon.has_food

        sr, stheta = spoon.length, spoon.theta
        sx, sy = polar_to_cartesian(sr, stheta)
        
        # get locations of all players with open mouth
        players_open = [self.players[f"player_{i}"] for i in range(self.n_seats) if self.players[f"player_{i}"].mouth_open]
        players_open_locs = []
        for p in players_open:
            pr, ptheta = p.location
            px, py = polar_to_cartesian(pr, ptheta)
            players_open_locs.append((px, py))

        players_fed = -1
        # compare distance between spoon head and open mouth players
        # are within the feed distance
        for j in range(len(players_open_locs)):
            px, py = players_open_locs
            if distance((sx, sy),(px, py)) <= self.feed_dist:
                players_fed = players_open[j].id
                break
        
        # return which player is fed and which spoon should be empty
        return players_fed
    
    def release_food(self, spoon_id):
        player_id = self.check_feed_range(spoon_id)
        if player_id != -1:
            player = self.players[player_id]
            player.hunger += 1

        spoon = self.spoons[spoon_id]
        food = self.foods[spoon.food_id]

        spoon.drop()
        food.reset()
        pass

    def check_pickup(self, spoon_id):
        """
        checks if spoon can pick up any food
        """
        spoon = self.spoons[spoon_id]
        sr, stheta = spoon.length, spoon.theta
        sx, sy = polar_to_cartesian(sr, stheta)

        player = self.players[f"player_{int(spoon.player_id)}"]
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

    def agent_iter(self):
        if self.check_terminal():
            raise StopIteration
        
        if self.player_ptr >= self.n_seats:
            self.player_ptr = 0
        else:
            self.player_ptr += 1
        self.t += 1
        return f"player_{int(self.player_ptr)}"
    
    def step(self, action):
        if action is None:
            return
        
        current_player = self.players[f"player_{int(self.player_ptr)}"]
        current_spoon = self.spoons[int(self.player_ptr)]

        spoon_length, spoon_theta, open_mouth, pick_food, drop_food = action

        # set spoon length and theta
        current_spoon.length, current_spoon.theta = spoon_length, spoon_theta

        # set current player mouth to open or closed
        current_player.mouth_open = open_mouth

        if pick_food:
            # if pick_food is True
            # check if it's possible to pick up food
            if self.check_pickup(current_spoon.id):
                # if so, pickup food
                self.pickup_food(current_spoon.id)

        if current_spoon.has_food:
            # if current spoon has food
            # check drop_food
            if drop_food:
                # if so, release food
                self.release_food()
        pass

    def last(self):
        obs_dict = self.observation(f"player_{int(self.player_ptr)}")
        termination = self.check_terminal()
        truncation = termination
        reward = self.rewards()[f"player_{int(self.player_ptr)}"]
        return obs_dict, reward, termination, truncation
    
    def reset(self):
        self.__init__(r=self.radius, 
                      n_seats=self.n_seats, 
                      max_spoon_angle=self.max_spoon_angle, 
                      feed_dist= self.feed_dist, 
                      include_other_rew=self.include_other_rew, 
                      max_timesteps=self.max_timesteps)

    def action_sample(self):
        sl_min, sl_max = self.action_space["spoon_length"]
        st_min, st_max = self.action_space["spoon_theta"]
        sl = random.uniform(sl_min, sl_max)
        st = random.uniform(st_min, st_max)
        o = random.random() > 0.5
        p = random.random() > 0.5
        d = random.random() > 0.5
        return sl, st, o, p, d

