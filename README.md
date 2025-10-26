# Block Blast - Enhanced Edition

A modern Tetris-inspired block puzzle game built with Python and Pygame.

## Features

- **Progressive Scoring**: 1 line = 100pts, 2 lines = 300pts, 3 lines = 600pts, 4+ lines = 1000pts+
- **Keyboard Controls**: Arrow keys for movement, R/B for rotation, Space to place
- **Number Key Selection**: Press 1, 2, or 3 to select blocks with preview
- **Visual Feedback**: Block previews, score popups, and combo effects
- **Multiple Game Modes**: Classic mode with more to come

## Controls

### Block Selection
- **1, 2, 3**: Select blocks (shows preview at cursor)
- **Mouse Click**: Select blocks in sidebar

### Movement
- **Arrow Keys**: Move cursor around grid
- **R or B**: Rotate selected block
- **Space**: Place block at cursor position
- **Mouse Click**: Place block at mouse position

### Game Controls
- **F5**: Reset game
- **P**: Pause/Unpause
- **Esc**: Quit game

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Atlasfailed/block-whacker.git
cd block-whacker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install pygame
```

4. Run the game:
```bash
./run_game.sh  # On Windows: python main_modular.py
```

## Game Mechanics

- **Line Clearing**: Complete horizontal or vertical lines to score points
- **Progressive Scoring**: Multiple lines cleared simultaneously give bonus points
- **Block Management**: Three blocks available at once, new set generated when all used
- **Preview System**: See where blocks will be placed before confirming

## Project Structure

```
src/
├── core/           # Game logic and data structures
├── ui/             # Rendering and input handling
├── audio/          # Sound management
└── utils/          # Utilities and file management
```

## Development

The game uses a modular architecture with separate managers for different concerns:
- **GameStateManager**: Handles game logic and scoring
- **GridManager**: Manages the game grid and line clearing
- **BlockManager**: Handles block generation and rotation
- **RendererManager**: Manages all visual rendering
- **InputHandler**: Processes keyboard and mouse input
- **AudioManager**: Handles sound effects and music
- **EffectsManager**: Manages visual effects and animations

## License

This project is open source. Feel free to modify and distribute.