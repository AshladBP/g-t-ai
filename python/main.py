import gym
import numpy as np
from ppo import Agent
import matplotlib.pyplot as plt

def plot_learning_curve(x, scores, labels, figure_file):
    plt.figure()
    for score, label in zip(scores, labels):
        plt.plot(x, score, label=label)
    plt.xlabel('Episode')
    plt.ylabel('Score')
    plt.title('Learning Curve')
    plt.legend()
    plt.savefig(figure_file)
    plt.show()  # To display the plot in addition to saving it
    plt.close()

if __name__ == '__main__':
    env = gym.make("ALE/Assault-v5", render_mode="human")
    N = 20
    batch_sizes = [64]  # Different batch sizes
    nb_epochs = 4
    alpha = 0.0003

    nb_games = 300
    figure_file = 'plots/cartpole_multiple_batch_sizes.png'

    all_score_histories = []
    labels = []

    for batch_size in batch_sizes:
        agent = Agent(nb_actions=env.action_space.n, batch_size=batch_size, alpha=alpha, nb_epochs=nb_epochs, input_dims=env.observation_space.shape)
        
        best_score = env.reward_range[0]
        score_history = []

        learn_iters = 0
        avg_score = 0
        curr_step = 0

        for i in range(nb_games):
            observation, _ = env.reset()
            done = False
            score = 0
            while not done:
                env.render()
                action, prob, val = agent.choose_action(observation)
                observation_, reward, done, info, _ = env.step(action)
                curr_step += 1
                score += reward
                agent.remember(observation, action, prob, val, reward, done)
                if curr_step % N == 0:
                    agent.learn()
                    learn_iters += 1
                observation = observation_
            score_history.append(score)
            avg_score = np.mean(score_history[-100:])
            print(f"Batch size {batch_size}, episode {i}: score {score}, avg_score {avg_score}, time_steps {curr_step}, learning_steps {learn_iters}")

        all_score_histories.append(score_history)
        labels.append(f'Batch size {batch_size}')

    x = [i+1 for i in range(nb_games)]
    plot_learning_curve(x, all_score_histories, labels, figure_file)
