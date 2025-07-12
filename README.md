# Circular Pong Game

A retro-style single-player game inspired by Pong, where the paddle moves along a semicircular arc and the ball bounces within a full circle.

## Features

- **Semicircular Paddle Movement**: Control a paddle that moves along the lower half of a circle (180° to 360°)
- **Circular Ball Physics**: Ball bounces off the circular boundary with realistic reflection physics
- **Survival Gameplay**: Prevent the ball from crossing the lower semicircle without being hit
- **Score System**: Track time survived and number of paddle bounces
- **Retro Aesthetics**: Green-on-black color scheme with glow effects

## Controls

- **Left Arrow**: Move paddle counterclockwise
- **Right Arrow**: Move paddle clockwise
- **R**: Restart game (when game over)
- **ESC**: Quit game

## Installation

1. Make sure you have Python 3.6+ installed
2. Install pygame:
   ```bash
   pip install -r requirements.txt
   ```
   Or directly:
   ```bash
   pip install pygame
   ```

## Running the Game

```bash
python circular_pong.py
```

## Gameplay

- The paddle moves along the bottom semicircle of the playing field
- The ball bounces off the circular boundary and the paddle
- If the ball crosses through the lower semicircle without hitting your paddle, you lose
- Try to survive as long as possible and rack up bounces!
- The red arc indicates the danger zone where the ball must not pass

## Code Structure

The game is organized into modular classes:

- `Ball`: Handles ball physics, movement, and circular boundary collision
- `Paddle`: Manages paddle movement along the semicircular arc
- `Game`: Main game logic, collision detection, scoring, and rendering

The code includes comprehensive comments explaining the physics calculations and game mechanics.

## Physics Details

- Ball reflection off circular boundary uses vector math for realistic bouncing
- Paddle collision detection uses point-to-line distance calculations
- Small random variations prevent predictable ball patterns
- Speed normalization maintains consistent ball velocity

Enjoy the game!
