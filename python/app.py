import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from env import CartPoleEnv
from ppo import Agent

def plot_chart(dataframe, x_col, y_col, title, x_label, y_label):
    base = alt.Chart(dataframe).encode(x=alt.X(x_col, title=x_label))

    line_spiky = base.mark_line(color='#ADD8E6', opacity=0.3).encode(
        y=alt.Y(y_col, title=y_label)
    )

    line_smooth = base.mark_line(color='#ADD8E6').transform_window(
        rolling_mean='mean(' + y_col + ')',
        frame=[-50, 50]
    ).encode(
        y='rolling_mean:Q'
    )

    return alt.layer(line_spiky, line_smooth).properties(title=title).interactive()

# Initialize environment and agent
env = CartPoleEnv()
agent = Agent(nb_actions=3, batch_size=64, alpha=0.0003, nb_epochs=4, input_dims=(4,))

# Streamlit app
st.title('Live Monitoring of PPO Training')

# Placeholders for the live charts
st.subheader('Actor Loss')
actor_loss_placeholder = st.empty()
actor_loss_value = st.text('Current Actor Loss: N/A')

st.subheader('Critic Loss')
critic_loss_placeholder = st.empty()
critic_loss_value = st.text('Current Critic Loss: N/A')

st.subheader('Rewards')
reward_placeholder = st.empty()
reward_value = st.text('Current Reward: N/A')

# Variables to store the losses and rewards
actor_losses = []
critic_losses = []
rewards = []
learning_steps = []
score_history = []

N = 50
max_time_steps = 500_000
curr_step = 0
curr_episode = 0
curr_learning_step = 0

while curr_step < max_time_steps:
    curr_episode += 1
    env.reset()
    observation, _, _ = env.step(0)
    done = False
    score = 0
    
    while not done:
        action, prob, val = agent.choose_action(observation)
        observation_, reward, done = env.step(action)
        if curr_episode % 100 == 0:
            env.render()
        score += reward
        agent.remember(observation, action, prob, val, reward, done)
        
        if curr_step % N == 0:
            curr_learning_step += 1
            agent.learn()
            # Collecting losses and rewards
            actor_losses.append(agent.actor_loss)
            critic_losses.append(agent.critic_loss)
            rewards.append(score)
            learning_steps.append(curr_learning_step)
            
            # Create dataframes for plotting
            actor_loss_df = pd.DataFrame({'Learning Step': learning_steps, 'Actor Loss': actor_losses})
            critic_loss_df = pd.DataFrame({'Learning Step': learning_steps, 'Critic Loss': critic_losses})
            reward_df = pd.DataFrame({'Learning Step': learning_steps, 'Reward': rewards})
            
            # Update charts
            actor_loss_chart = plot_chart(actor_loss_df, 'Learning Step', 'Actor Loss', 'Actor Loss over Time', 'Learning Steps', 'Actor Loss')
            critic_loss_chart = plot_chart(critic_loss_df, 'Learning Step', 'Critic Loss', 'Critic Loss over Time', 'Learning Steps', 'Critic Loss')
            reward_chart = plot_chart(reward_df, 'Learning Step', 'Reward', 'Reward over Time', 'Learning Steps', 'Reward')

            actor_loss_placeholder.altair_chart(actor_loss_chart, use_container_width=True)
            actor_loss_value.text(f'Current Actor Loss: {agent.actor_loss:.4f}')
            
            critic_loss_placeholder.altair_chart(critic_loss_chart, use_container_width=True)
            critic_loss_value.text(f'Current Critic Loss: {agent.critic_loss:.4f}')
            
            reward_placeholder.altair_chart(reward_chart, use_container_width=True)
            reward_value.text(f'Current Reward: {score:.4f}')
        
        observation = observation_
        curr_step += 1
    
    if curr_step % N != 0:
        score_history.append(score)

# To keep the app running
while True:
    time.sleep(1)
