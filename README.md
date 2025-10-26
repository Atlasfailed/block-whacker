# Block Whacker - Web Edition

A modern block puzzle game with touch controls, optimized for mobile play. Built with vanilla JavaScript and HTML5 Canvas.

🎮 **[Play Now!](https://atlasfailed.github.io/block-whacker/)**

## Features

- ✨ **Mobile-First Design**: Optimized touch controls with drag-and-drop
- 🎯 **Smart Snapping**: Intelligent block placement assistance
- ↩️ **Undo System**: One-time undo for the last placed block
- 🎨 **40+ Block Variations**: Pre-rotated shapes for easy placement
- 📱 **Responsive Layout**: Works on all screen sizes
- 🏗️ **Modular Architecture**: Clean ES6 module structure

## How to Play

1. **Select a Block**: Tap/click one of the three blocks at the bottom
2. **Drag to Place**: Drag the block to your desired position on the grid
3. **Smart Placement**: The block will snap to the nearest valid position
4. **Clear Lines**: Complete rows or columns to score points and clear space
5. **Keep Going**: When all three blocks are used, you get three new ones

## Controls

### Touch/Mouse
- **Tap/Click**: Select a block from the preview boxes
- **Drag**: Move the block around the grid
- **Release**: Place the block at the snapped position

### Buttons
- **↩️ Undo**: Undo the last placement (one-time use per placement)
- **🔄 Reset**: Start a new game

### Keyboard (Desktop)
- **Arrow Keys**: Move cursor
- **Space/Enter**: Place selected block
- **Escape**: Deselect block

## Scoring

- **1 line**: 100 points × level
- **2 lines**: 300 points × level  
- **3 lines**: 600 points × level
- **4+ lines**: 1000+ points × level

## Project Structure

\`\`\`
web/
├── index.html              # Main HTML file
├── js/
│   ├── main.js            # Entry point
│   ├── classes/
│   │   ├── Game.js        # Core game logic
│   │   ├── Block.js       # Block shapes and generation
│   │   ├── InputHandler.js # Event handling
│   │   └── Renderer.js    # Canvas rendering
│   └── utils/
│       ├── constants.js   # Configuration
│       └── coordinates.js # Coordinate utilities
└── README.md
\`\`\`

## Technical Details

### Key Features Implemented

1. **Coordinate Scaling**: Proper transformation between display and canvas coordinates
2. **Dynamic Finger Offset**: Blocks positioned above finger/cursor for visibility
3. **Smart Snapping Algorithm**: Manhattan distance search with Euclidean distance selection
4. **Deep State Management**: Full game state capture for undo functionality
5. **ES6 Modules**: Modern JavaScript with proper separation of concerns

### Mobile Optimizations

- Touch event handling with \`{passive: false}\` for drag prevention
- Dynamic offset based on block height (taller blocks = higher offset)
- 8×8 grid size for larger, easier-to-tap cells
- Full-width grid layout for maximum playable area
- Square canvas (420×420) matching grid proportions

## Development

### Running Locally

Simply open \`web/index.html\` in a modern browser, or use a local server:

\`\`\`bash
cd web
python -m http.server 8000
# Visit http://localhost:8000
\`\`\`

### Deployment

The game is automatically deployed to GitHub Pages from the \`web/\` directory.

## Archive

Legacy Python/Pygame versions and the original monolithic JavaScript version are archived in the \`archive/\` folder.

## License

MIT License - See LICENSE file for details

## Credits

Created by Atlasfailed
- Repository: https://github.com/Atlasfailed/block-whacker
- Live Demo: https://atlasfailed.github.io/block-whacker/
