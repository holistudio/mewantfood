# PlayFoodAgent picks up food and just waves it around never dropping it
class PlayFoodAgent(object):
    def __init__(self, action_space):
        self.timer = 0
        self.min_spoon_len = action_space["spoon_length"][0]
        self.max_spoon_len = action_space["spoon_length"][1]

        self.action_space = action_space
        self.current_action = {
            "spoon_length": (self.min_spoon_len + self.max_spoon_len)/2,
            "spoon_theta": 0,
            "open_mouth": False,
            "pick_food": False,
            "drop_food": False # this is masked from the player unless they have food on their spoon
        }
        pass
    
    def step(self, observation):
        self.current_action = {
            "spoon_length": self.min_spoon_len,
            "spoon_theta": 0,
            "open_mouth": False,
            "pick_food": False,
            "drop_food": False # this is masked from the player unless they have food on their spoon
        }

        # step 1: set spoon_length to min_spoon length
        if self.timer == 1:
            self.current_action["spoon_length"] = self.min_spoon_len
        
        # step 2: pick up food
        if self.timer == 2:
            self.current_action["pick_food"] = True

        # step 3-4: shift spoon theta + 1
        if 3 <= self.timer < 5:
            self.current_action["spoon_theta"] = 1

        # step 5-8: shift spoon theta - 1
        if 5 <= self.timer < 9:
            self.current_action["spoon_theta"] = -1
        # step 9-12: shift spoon theta - 1
        if 9 <= self.timer < 13:
            self.current_action["spoon_theta"] = +1

        if self.timer < 12:
            self.timer += 1
        else:
            self.timer = 5
        return self.current_action["spoon_length"], self.current_action["spoon_theta"], self.current_action["open_mouth"], self.current_action["pick_food"], self.current_action["drop_food"]
    

# TODO: GenerousAgent always picks up food and feeds ito the agent across from it

class GenerousAgent(object):
    def __init__(self, action_space):
        self.timer = 0
        self.min_spoon_len = action_space["spoon_length"][0]
        self.max_spoon_len = action_space["spoon_length"][1]

        self.action_space = action_space
        self.current_action = {
            "spoon_length": (self.min_spoon_len + self.max_spoon_len)/2,
            "spoon_theta": 0,
            "open_mouth": False,
            "pick_food": False,
            "drop_food": False # this is masked from the player unless they have food on their spoon
        }
        pass
    
    def step(self, observation):
        self.current_action = {
            "spoon_length": self.min_spoon_len,
            "spoon_theta": 0,
            "open_mouth": False,
            "pick_food": False,
            "drop_food": False # this is masked from the player unless they have food on their spoon
        }

        # step 1: set spoon_length to min_spoon_length
        if self.timer == 1:
            self.current_action["spoon_length"] = self.min_spoon_len
        
        # step 2: pick up food
        if self.timer == 2:
            self.current_action["pick_food"] = True

        # step 3: set spoon length to max_spoon_length
        if self.timer == 3:
            self.current_action["spoon_length"] = self.max_spoon_len

        # step 4: drop food
        if self.timer == 4:
            self.current_action["spoon_length"] = self.max_spoon_len
            self.current_action["drop_food"] = True

        if self.timer < 4:
            self.timer += 1
        else:
            self.timer = 1
        return self.current_action["spoon_length"], self.current_action["spoon_theta"], self.current_action["open_mouth"], self.current_action["pick_food"], self.current_action["drop_food"]

# TODO: TitTatAgent will behave like GenerousAgent only after it gets fed