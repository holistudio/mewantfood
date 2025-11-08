from environment import Environment

env = Environment(r=180, n_seats=4)

env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation = env.last()

    if termination or truncation:
        action = None
    else:
        # this is where you would insert your policy
        action = env.action_sample()

    env.step(action)

print(env.rewards())

env.save_info()
env.save_log()
env.reset()