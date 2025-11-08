from environment import Environment

env = Environment(r=5, n_seats=4)

env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation = env.last()

    if termination or truncation:
        action = None
    else:
        # this is where you would insert your policy
        action = env.action_sample()

    env.step(action)