import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from env import CartPoleEnv
from ppo import Agent
import torch as T

def plot_chart(dataframe, x_col, y_col, title, x_label, y_label, rolling_frame=50):
    base = alt.Chart(dataframe).encode(x=alt.X(x_col, title=x_label))

    line_spiky = base.mark_line(color='#ADD8E6', opacity=0.3).encode(
        y=alt.Y(y_col, title=y_label)
    )

    line_smooth = base.mark_line(color='#ADD8E6').transform_window(
        rolling_mean='mean(' + y_col + ')',
        frame=[-rolling_frame, rolling_frame]
    ).encode(
        y='rolling_mean:Q'
    )

    return alt.layer(line_spiky, line_smooth).properties(title=title).interactive()

# Initialize environment and agent
env = CartPoleEnv()
agent = Agent(nb_actions=3, batch_size=64, alpha=0.0003, nb_epochs=4, input_dims=(4,))

# Streamlit app
st.set_page_config(layout='wide')
st.title('Live Monitoring of PPO Training')

# Create a grid layout with three charts and three buttons
col1, col2 = st.columns(2)

with col1:
    st.subheader('Actor Loss')
    actor_loss_placeholder = st.empty()
    actor_loss_value = st.text('Current Actor Loss: N/A')

with col2:
    st.subheader('Critic Loss')
    critic_loss_placeholder = st.empty()
    critic_loss_value = st.text('Current Critic Loss: N/A')

col3, col4 = st.columns(2)

with col3:
    st.subheader('Rewards')
    reward_placeholder = st.empty()
    reward_value = st.text('Current Reward: N/A')

with col4:
    st.subheader('Controls')
    start_button = st.button('Start Training')
    pause_button = st.button('Pause Training')
    save_button = st.button('Save Model')

# File uploaders for models
actor_model_uploader = st.file_uploader("Upload Actor Model", type=["pth", "pt"])
critic_model_uploader = st.file_uploader("Upload Critic Model", type=["pth", "pt"])

# Load models if files are uploaded
if actor_model_uploader is not None and critic_model_uploader is not None:
    st.write("Loading models...")
    actor_model_path = f"uploaded_actor_model.pth"
    critic_model_path = f"uploaded_critic_model.pth"
    
    with open(actor_model_path, "wb") as f:
        f.write(actor_model_uploader.getbuffer())
        
    with open(critic_model_path, "wb") as f:
        f.write(critic_model_uploader.getbuffer())
    
    agent.actor.load_state_dict(T.load(actor_model_path))
    agent.critic.load_state_dict(T.load(critic_model_path))
    st.write("Models loaded successfully!")

# Variables to store the losses and rewards
actor_losses = []
critic_losses = []
episode_rewards = []
episodes = []
score_history = []

# Flags for controlling training
training = False
paused = False

N = 500
max_time_steps = 500_000
curr_step = 0
curr_episode = 0
curr_learning_step = 0

if start_button:
    st.write('Training Started')
    training = True
    paused = False

if pause_button:
    st.write('Training Paused')
    paused = True

if save_button:
    st.write('Model Saved')
    agent.save_models()

while curr_step < max_time_steps:
    if training and not paused:
        curr_episode += 1
        env.reset()
        observation, _, _ = env.step(0)
        done = False
        score = 0

        while not done:
            action, prob, val = agent.choose_action(observation)
            observation_, reward, done = env.step(action)
            env.render(quick=False)
            score += reward
            agent.remember(observation, action, prob, val, reward, done)

            if curr_step % N == 0:
                curr_learning_step += 1
                agent.learn()
                # Collecting losses
                actor_losses.append(agent.actor_loss)
                critic_losses.append(agent.critic_loss)

                # Create dataframes for plotting
                actor_loss_df = pd.DataFrame({'Learning Step': list(range(len(actor_losses))), 'Actor Loss': actor_losses})
                critic_loss_df = pd.DataFrame({'Learning Step': list(range(len(critic_losses))), 'Critic Loss': critic_losses})

                # Update charts
                actor_loss_chart = plot_chart(actor_loss_df, 'Learning Step', 'Actor Loss', 'Actor Loss over Time', 'Learning Steps', 'Actor Loss')
                critic_loss_chart = plot_chart(critic_loss_df, 'Learning Step', 'Critic Loss', 'Critic Loss over Time', 'Learning Steps', 'Critic Loss')

                actor_loss_placeholder.altair_chart(actor_loss_chart, use_container_width=True)
                actor_loss_value.text(f'Current Actor Loss: {agent.actor_loss:.4f}')

                critic_loss_placeholder.altair_chart(critic_loss_chart, use_container_width=True)
                critic_loss_value.text(f'Current Critic Loss: {agent.critic_loss:.4f}')

                # Save models every 100 learning steps
                if curr_learning_step % 100 == 0:
                    agent.save_models()

            observation = observation_
            curr_step += 1

        episode_rewards.append(score)
        episodes.append(curr_episode)

        reward_df = pd.DataFrame({'Episode': episodes, 'Reward': episode_rewards})
        reward_chart = plot_chart(reward_df, 'Episode', 'Reward', 'Reward over Episodes', 'Episodes', 'Reward', rolling_frame=10)

        reward_placeholder.altair_chart(reward_chart, use_container_width=True)
        reward_value.text(f'Current Reward: {score:.4f}')

    time.sleep(1)