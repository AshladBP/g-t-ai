import sys
from pygame_env import PlayerEnv
import numpy as np
from ppo import Agent

import matplotlib.pyplot as plt

def plot_learning_curve(learning_steps, scores, avg_last_10_scores, labels, figure_file):
    plt.figure()
    for ls, score, avg_score, label in zip(learning_steps, scores, avg_last_10_scores, labels):
        min_length = min(len(ls), len(score))
        plt.plot(ls[:min_length], score[:min_length], label=f'{label} Score', linestyle='--')
        if len(avg_score) > 0:
            plt.plot(ls[:len(avg_score)], avg_score, label=f'{label} Avg last 10')
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
        N = 50
        batch_sizes = [32, 64, 128, 256, 1024]  # Different batch sizes
        nb_epochs = 4
        alpha = 0.0003
        max_time_steps = 500_000
        figure_file = 'plots/playerenv_multiple_batch_sizes.png'

        all_learning_steps = []
        all_score_histories = []
        all_avg_last_10_histories = []
        labels = []

        for batch_size in batch_sizes:
            agent = Agent(nb_actions=4, batch_size=batch_size, alpha=alpha, nb_epochs=nb_epochs, input_dims=(2,))
            score_history = []
            avg_last_10_scores = []
            learning_steps = []

            learn_iters = 0
            curr_step = 0
            curr_episode = 0

            while curr_step < max_time_steps:
                curr_episode += 1
                observation = env.reset()
                done = False
                score = 0
                while not done:
                    env.render()  # Render the environment
                    action, prob, val = agent.choose_action(observation)
                    observation_, reward, done = env.step(action)
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

            all_learning_steps.append(learning_steps)
            all_score_histories.append(score_history)
            all_avg_last_10_histories.append(avg_last_10_scores)
            labels.append(f'Batch size {batch_size}')

        plot_learning_curve(all_learning_steps, all_score_histories, all_avg_last_10_histories, labels, figure_file)
    except KeyboardInterrupt:
        env.close()
        print("Environment closed.")
        sys.exit(0)