# This file contains the options that you should modify to solve Question 2

# Here the agent wants to reach the close exit (+1) as quickly as possible (no risk of cliff)
def question2_1():
    return {
        "noise": 0,
        "discount_factor": 0.1,
        "living_reward": 0
    }

# Here the agent wants to reach the close exit (+1) as quickly as possible (with risk of cliff, so we add some noise)
def question2_2():
    return {
        "noise": 0.1,
        "discount_factor": 0.1,
        "living_reward": -0.1
    }

# Here the agent wants to reach the distant exit (+10) as quickly as possible (no risk of cliff)
def question2_3():
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": -0.1
    }

# Here the agent wants to reach the distant exit (+10) as quickly as possible (with risk of cliff, so we add some noise)
def question2_4():
        return {
        "noise": 0.2,
        "discount_factor": 1,
        "living_reward": -0.1
    }

# Here the agent wants to avoid both exits and the cliff (so it prefers to live forever)
def question2_5():
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": 10
    }

# Here the agent wants to end the game as quickly as possible
def question2_6():
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": -100
    }