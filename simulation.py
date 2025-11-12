from environment import Environment
from agent import PlayFoodAgent
env = Environment(r=180, n_seats=4)

agent1 = PlayFoodAgent(env.action_space)

agents = [agent1, None, None, None]

env.reset()
a_i = 0

for player_name in env.agent_iter():
    agent = agents[a_i]

    observation, reward, termination, truncation = env.last()

    if termination or truncation:
        action = None
    else:
        if agent is None:
            action = env.action_sample()
        else:
            action = agent.step(observation)

    env.step(action)

    if a_i < len(agents)-1:
        a_i += 1
    else:
        a_i = 0

print(env.rewards())

env.save_info()
env.save_log()
env.reset()