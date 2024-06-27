Hyperion Alpha README

---

Game Overview
This is a Pygame-based top-down shooter game where the player navigates through a map, avoiding obstacles and defeating enemies. The game currently features collision detection, advanced movement, projectile weapons, procedurally generated enviroments, enemy AI, and a pause functionality.

Features
- Player Movement: Move the player using the W, A, S, and D keys.
- Enemy AI: Enemies navigate the map and try to reach the player, avoiding obstacles using basic pathfinding logic.
- Projectiles: Both player and enemies can shoot projectiles, which collide with walls and other game objects.
- Pause Functionality: Pause the game by pressing 'P' and resume by pressing 'Enter'.
- Health Pickups: Collect health pickups to restore player health.

Controls
- Movement: W, A, S, D keys
- Shoot: Left mouse button
- Switch Weapon: 1, 2, 3 keys
- Dash: Spacebar
- Pause: P key
- Resume: Enter key
- Exit: Esc key

Installation
1. Ensure you have Python and Pygame installed. If not, you can install Pygame using:
    ```bash
    pip install pygame
    ```
2. Clone the repository or download the source code.

Running the Game
Navigate to the directory containing the game files and run the following command:
```bash
python main.py
```

File Descriptions
- main.py: Contains the main game loop and handles game initialization, event processing, and game state updates.
- src.py: Contains the game classes, including `Player`, `Enemy`, `Projectile`, and `Wall`. Implements game logic and AI.
- ui.py: Handles user interface elements such as the pause screen and health bar.

Game Classes and Methods

Player Class
- Attributes: Position, speed, health, stamina, weapons.
- Methods: `move()`, `shoot()`, `take_damage()`, `dash()`, `update_stamina()`, `draw_dash_effect()`, `aim()`.

Enemy Class
- Attributes: Position, speed, health, shoot timer.
- Methods: `follow_player()`, `shoot()`, `take_damage()`, `collide_with_walls()`, `a_star()` (for pathfinding).

Projectile Class
- Attributes: Position, speed, angle.
- Methods: `update()`, `collide_with_walls()`.

Wall Class
- Attributes: Position, size.
- Methods: None (just for collision detection).

Known Issues
- Enemies may occasionally get stuck in corners or on each other. The current implementation includes basic pathfinding and random movement to mitigate this issue.

Contributing
Feel free to submit issues, fork the repository, and make pull requests. Contributions are welcome!

License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

Enjoy playing the game! If you encounter any bugs or have any suggestions, please open an issue or contact the project maintainer.