from flask import Flask, render_template, jsonify, request, send_file
import numpy as np
import pandas as pd
import altair as alt
from agents.ppo import Agent
from envs.player_env import PlayerEnv
import threading
import time
import os
import io

app = Flask(__name__)

# parametres
batch_size = 1024 
nb_epochs = 4
learning_rate = 0.0003

# Variables globales
env = PlayerEnv()
agent = Agent(nb_actions=4, batch_size=batch_size, alpha=learning_rate, nb_epochs=nb_epochs, input_dims=(10,))
actor_losses = []
critic_losses = []
rewards = []
learning_steps = []
is_training = False
training_thread = None
is_rendering = False

def training_loop():
    global is_training, actor_losses, critic_losses, rewards, learning_steps, is_rendering
    step = 0
    episode = 0
    learning_step = 0
    while is_training:
        episode += 1
        observation = env.reset()
        done = False
        episode_reward = 0
        while not done and is_training:
            action, prob, val = agent.choose_action(observation)
            observation_, reward, done = env.step(action)
            if is_rendering:
                env.render()
            step += 1
            episode_reward += reward
            agent.remember(observation, action, prob, val, reward, done)
            if step % batch_size == 0:
                agent.learn()
                actor_losses.append(agent.actor_loss)
                critic_losses.append(agent.critic_loss)
                learning_step += 1
                learning_steps.append(learning_step)
            observation = observation_
        rewards.append(episode_reward)
        time.sleep(0.01)  # Pour éviter de surcharger le CPU

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/start_training', methods=['POST'])
def start_training():
    global is_training, training_thread
    if not is_training:
        is_training = True
        training_thread = threading.Thread(target=training_loop)
        training_thread.start()
        return jsonify({"status": "Training started"})
    return jsonify({"status": "Training already in progress"})

@app.route('/stop_training', methods=['POST'])
def stop_training():
    global is_training
    is_training = False
    if training_thread:
        training_thread.join()
    return jsonify({"status": "Training stopped"})

@app.route('/toggle_rendering', methods=['POST'])
def toggle_rendering():
    global is_rendering
    is_rendering = not is_rendering
    return jsonify({"status": "Rendering toggled", "is_rendering": is_rendering})

@app.route('/get_data')
def get_data():
    global actor_losses, critic_losses, rewards, learning_steps

    if not learning_steps or not rewards:
        return jsonify({
            'actor_chart': {},
            'critic_chart': {},
            'reward_chart': {}
        })

    loss_window = min(20, len(actor_losses))
    reward_window = min(50, len(rewards))

    # Calculer la moyenne mobile
    if len(actor_losses) >= loss_window:
        actor_rolling = np.convolve(actor_losses, np.ones(loss_window)/loss_window, mode='valid')
        critic_rolling = np.convolve(critic_losses, np.ones(loss_window)/loss_window, mode='valid')
    else:
        actor_rolling = actor_losses
        critic_rolling = critic_losses

    if len(rewards) >= reward_window:
        reward_rolling = np.convolve(rewards, np.ones(reward_window)/reward_window, mode='valid')
    else:
        reward_rolling = rewards

    # Créer les dataframes
    actor_df = pd.DataFrame({
        'step': learning_steps,
        'loss': actor_losses,
        'rolling': np.pad(actor_rolling, (len(actor_losses) - len(actor_rolling), 0), mode='edge')
    })
    critic_df = pd.DataFrame({
        'step': learning_steps,
        'loss': critic_losses,
        'rolling': np.pad(critic_rolling, (len(critic_losses) - len(critic_rolling), 0), mode='edge')
    })
    reward_df = pd.DataFrame({
        'episode': range(len(rewards)),
        'reward': rewards,
        'rolling': np.pad(reward_rolling, (len(rewards) - len(reward_rolling), 0), mode='edge')
    })

    # Créer les graphiques Altair
    base_actor = alt.Chart(actor_df).encode(x='step')
    actor_chart = base_actor.mark_line(color='lightblue', opacity=0.5).encode(
        y='loss'
    ) + base_actor.mark_line(color='blue').encode(
        y='rolling'
    ).properties(title='Actor Loss').interactive()

    base_critic = alt.Chart(critic_df).encode(x='step')
    critic_chart = base_critic.mark_line(color='lightgreen', opacity=0.5).encode(
        y='loss'
    ) + base_critic.mark_line(color='green').encode(
        y='rolling'
    ).properties(title='Critic Loss').interactive()

    base_reward = alt.Chart(reward_df).encode(x='episode')
    reward_chart = base_reward.mark_line(color='pink', opacity=0.5).encode(
        y='reward'
    ) + base_reward.mark_line(color='red').encode(
        y='rolling'
    ).properties(title='Rewards').interactive()

    return jsonify({
        'actor_chart': actor_chart.to_dict(),
        'critic_chart': critic_chart.to_dict(),
        'reward_chart': reward_chart.to_dict()
    })

@app.route('/save_model', methods=['POST'])
def save_model():
    global agent
    agent.save_models()
    return jsonify({"status": "Model saved successfully"})

@app.route('/load_model', methods=['POST'])
def load_model():
    global agent
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    model_type = request.form.get('model_type')
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and model_type:
        # Save the uploaded file temporarily
        file_path = os.path.join('temp', file.filename)
        file.save(file_path)
        # Load the model
        if model_type == 'actor':
            agent.load_actor_model(file_path)
        elif model_type == 'critic':
            agent.load_critic_model(file_path)
        else:
            return jsonify({"error": "Invalid model type"}), 400
        # Remove the temporary file
        os.remove(file_path)
        return jsonify({"status": f"{model_type.capitalize()} model loaded successfully"})

@app.route('/get_model', methods=['GET'])
def get_model():
    global agent
    actor_data, critic_data = agent.get_model_data()
    return jsonify({
        'actor_model': actor_data.decode('latin-1'),
        'critic_model': critic_data.decode('latin-1')
    })


@app.route('/level_selector')
def level_selector():
    levels = ['Level 1', 'Level 2', 'Level 3']  # Replace with your actual levels
    return render_template('level_selector.html', levels=levels)

if __name__ == '__main__':
    app.run(debug=True)

