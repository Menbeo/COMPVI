# Catch Your Professor!

**Catch Your Professor!** is an interactive hand-tracking game built with Python, Pygame, OpenCV, and MediaPipe. Players use their webcam to control a hand cursor on the screen, catching falling professor images while avoiding unwanted objects (e.g., failing scores). The game features multiple levels, a high score system, and a fun, engaging interface with custom graphics and sound effects.

## Features
- **Hand Tracking**: Uses MediaPipe to track hand movements via webcam, allowing players to catch professors by closing their hand.
- **Dynamic Gameplay**: Three levels with increasing difficulty, faster fall speeds, and more unwanted objects.
- **Professor Selection**: Players choose 1–3 professors to catch, with unique images for each.
- **High Scores**: Saves and displays the top 5 scores with player names.
- **Custom Assets**: Includes custom images (e.g., professor portraits, hearts, hand cursor) and sound effects (e.g., background music, level-up sounds).
- **User Interface**: Guide screen, name input, professor selection, and end screen with high scores.

## Prerequisites
To run the game, you need:
- **Python 3.7+**
- A webcam for hand tracking
- Required Python libraries (see [Dependencies](#dependencies))
- Game assets (images and sounds) in the correct folder structure

## Installation
1. **Clone or Download the Repository**:
   - Clone this repository or download the code files.
   ```bash
   git clone <repository-url>
   cd catch-your-professor
   ```

2. **Set Up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install the required Python libraries using `pip`:
   ```bash
   pip install pygame opencv-python mediapipe numpy
   ```

4. **Optional: Custom Font**:
   - The game uses `Minecraft.ttf` for text rendering. Place this font file in the project root, or the game will fall back to the system’s Arial font.

5. **Run the Game**:
   ```bash
   python main.py
   ```

## How to Play
1. **Guide Screen**:
   - The game starts with a welcome screen. Click the "Next" button to proceed.
2. **Ready Screen**:
   - Enter your name (up to 20 characters).
   - Select 1–3 professors by clicking their images. Selected professors will appear as falling objects.
   - Click "Start" to begin the game (enabled only if a name is entered and at least one professor is selected).
3. **Main Game**:
   - Use your webcam to control a hand cursor (displayed as `hand.png`).
   - Move your hand to align with falling professor images and close your hand (make a fist) to catch them.
   - Avoid catching unwanted objects (e.g., `fscore.png`), which deduct a life.
   - The game has three levels:
     - **Level 1**: Score > 10 to advance.
     - **Level 2**: Score > 20 to advance, faster fall speed, more unwanted objects.
     - **Level 3**: Even faster fall speed, more unwanted objects.
   - You have 3 lives and a 45-second timer (reduced in higher levels).
   - Game ends if time runs out or lives reach zero, showing `out_time.png` or `out_lives.png`.
4. **End Screen**:
   - Displays your score and the top 5 high scores.
   - Click anywhere to return to the guide screen.

## Controls
- **Mouse**:
  - Click "Next" on the guide screen.
  - Click to select professors or start the game on the ready screen.
  - Click to continue on the end screen.
- **Keyboard**:
  - Type your name in the ready screen.
  - Press `Enter` to start the game if conditions are met.
  - Press `Backspace` to delete characters in the name input.
- **Hand Gestures** (via webcam):
  - Move your hand to control the cursor.
  - Close your hand (fist) to catch professors.
- **Quit**:
  - Close the window or press the window’s close button to exit.

## Dependencies
- **pygame**: For game rendering, sound, and event handling.
- **opencv-python**: For webcam capture and hand tracking visualization.
- **mediapipe**: For real-time hand tracking.
- **numpy**: For numerical operations (e.g., random positions, distance calculations).

Install them with:
```bash
pip install pygame opencv-python mediapipe numpy
```

## Notes
- **Webcam**: Ensure your webcam is working and accessible. The game uses a resolution of 640x480.
- **Assets**: Missing assets will cause a `pygame.error` and exit the game. Verify all images and sounds are in `assets/images/` and `assets/sounds/`.
- **High Scores**: Stored in `high_scores.txt` in the project root. The file is created automatically if it doesn’t exist. Malformed lines are skipped.
- **Performance**: The game runs at 60 FPS. If lag occurs, ensure your system meets the requirements for real-time hand tracking.
- **Hand Tracking**: Adjust lighting and webcam positioning for optimal MediaPipe performance. The hand cursor is centered using `hand.png` (89x89 pixels).

## Troubleshooting
- **Error: "Error loading assets"**:
  - Check that all image and sound files are in the correct `assets/` subfolders.
  - Verify file names match those in the code.
- **Hand Tracking Not Working**:
  - Ensure your webcam is connected and not used by another application.
  - Check lighting conditions and hand visibility.
- **Game Crashes on High Score Load**:
  - Inspect `high_scores.txt` for malformed lines (should be `name:score` format).
  - Delete the file to start fresh if issues persist.
- **Font Missing**:
  - If `Minecraft.ttf` is missing, the game uses Arial. Place the font in the project root to use it.

## Future Improvements
- Add difficulty settings (e.g., adjustable fall speed or catch distance).
- Support multiple hand states (e.g., different images for open/closed hands).
- Improve hand tracking accuracy with more robust gesture detection.
- Add animations for catching professors or level transitions.
- Include a pause menu or settings screen.

## Credits
- Developed as part of a computer vision project.
- Uses MediaPipe for hand tracking and Pygame for game development.
- Custom assets (images, sounds) created for the game.

## License
This project is for educational purposes. Assets may be subject to their own licensing terms. Contact the developer for usage permissions.

---

Happy catching! If you have questions or need help, open an issue or contact the developer.