from time import sleep
from pygame_env import PlayerEnv
import numpy as np
from ppo import Agent
import matplotlib.pyplot as plt

LOAD = True
SAVE = False
RENDER = True

def plot_learning_curve(learning_steps, scores, avg_last_10_scores, label, figure_file):
    plt.figure()
    min_length = min(len(learning_steps), len(scores))
    plt.plot(learning_steps[:min_length], scores[:min_length], label=f'{label} Score', linestyle='--')
    if len(avg_last_10_scores) > 0:
        plt.plot(learning_steps[:len(avg_last_10_scores)], avg_last_10_scores, label=f'{label} Avg last 10')
    plt.xlabel('Learning Steps')
    plt.ylabel('Score')
    plt.xscale('log')
    plt.title('Learning Curve')
    plt.legend()
    plt.savefig(figure_file)
    plt.show()
    plt.close()

if __name__ == '__main__':
    try:
        env = PlayerEnv()
        N = 1024
        batch_size = 1024 
        nb_epochs = 4
        alpha = 0.0003
        max_time_steps = 500_000
        figure_file = 'plots/cartpole_single_batch_size.png'

        learning_steps = []
        score_history = []
        avg_last_10_scores = []
        label = f'Batch size {batch_size}'

        agent = Agent(nb_actions=4, batch_size=batch_size, alpha=alpha, nb_epochs=nb_epochs, input_dims=(12,))
        if LOAD:
            agent.load_models()
        learn_iters = 0
        curr_step = 0
        curr_episode = 0

        while curr_step < max_time_steps:
            curr_episode += 1
            env.reset()
            observation, _, _ = env.step(0)
            done = False
            score = 0
            while not done:
                action, prob, val = agent.choose_action(observation)
                observation_, reward, done = env.step(action)
                if RENDER:
                    env.render()
                score += reward
                agent.remember(observation, action, prob, val, reward, done)
                if curr_step % N == 0:
                    agent.learn()
                    learn_iters += 1
                    learning_steps.append(curr_step)
                    if score_history:
                        score_history.append(score_history[-1])  # Append the most recent episode score
                        if len(score_history) >= 10:
                            avg_last_10_scores.append(np.mean(score_history[-10:]))
                        else:
                            avg_last_10_scores.append(np.mean(score_history[:len(score_history)]))
                observation = observation_
                curr_step += 1

            if curr_step % N != 0:
                score_history.append(score)
                if len(score_history) >= 10:
                    avg_last_10_scores.append(np.mean(score_history[-10:]))
                else:
                    avg_last_10_scores.append(np.mean(score_history[:len(score_history)]))
                learning_steps.append(curr_step)

            print(f"Batch size {batch_size}, episode {curr_episode}: score {score}, time_steps {curr_step}, learning_steps {learn_iters}")

        plot_learning_curve(learning_steps, score_history, avg_last_10_scores, label, figure_file)
    except KeyboardInterrupt:
        env.close()
        if SAVE:
            agent.save_models()
        exit(0)