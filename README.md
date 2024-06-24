WARINING: the back to menu buttons don't always work and sometimes crash. The bug is known,sorry for the disagreement.

## Features

- Custom game environment built with Pygame
- AI agent implementation using PPO algorithm
- Level editor for creating custom levels
- Multiple game modes: Player, AI Training, and Level Editor
- Save and load AI models
- Visualize AI training progress

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/AshladBP/g-t-AI.git
   cd g-t-ai
   cd python
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script to start the application:

```
python main.py
```

### Game Modes

1. **Player Mode**: Play the game manually using arrow keys.
2. **AI Mode**: Train an AI agent using PPO algorithm.
3. **Level Editor**: Create and edit custom levels.

### Controls

- Use arrow keys to move the player in Player Mode.
- In AI Mode:
  - Space: Pause/Resume training
  - R: Toggle rendering
  - Click on buttons to save/load models or return to the main menu

## Project Structure

- `main.py`: Main entry point of the application
- `game.py`: Implements the core game logic and rendering
- `player_mode.py`: Handles the player-controlled game mode
- `ai_mode.py`: Manages the AI training mode
- `level_editor.py`: Provides a GUI for creating and editing levels
- `player_env.py`: Defines the environment for the AI agent
- `agents/ppo.py`: Implements the PPO algorithm for AI training

## Creating Custom Levels

1. Select "Level Editor" from the main menu.
2. Use the tools provided to create walls, set spawn points, and place goals.
3. Save your level with a unique name.

## Training AI Models

1. Select "AI Mode" from the main menu.
2. Choose a level for training.
3. Monitor the training progress and use the provided controls to manage the process.
4. Save your trained model for later use.
