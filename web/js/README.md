# Block Whacker - Modular JavaScript Structure

## Directory Structure

```
js/
├── main.js                 # Entry point, initializes the game
├── classes/
│   ├── Game.js            # Main game logic and state management
│   ├── Block.js           # Block class with all shape definitions
│   ├── InputHandler.js    # Mouse, touch, and keyboard input handling
│   └── Renderer.js        # Canvas rendering and drawing methods
└── utils/
    ├── constants.js       # Game configuration and color constants
    └── coordinates.js     # Coordinate transformation utilities
```

## Module Responsibilities

### `main.js`
- Application entry point
- Creates game instance when DOM is ready
- Minimal bootstrapping code

### `classes/Game.js`
- Core game state (score, grid, blocks, cursor position)
- Game loop orchestration
- Block placement and validation logic
- Line clearing and scoring
- Undo functionality
- UI updates

### `classes/Block.js`
- Defines all block shapes (40+ variations)
- Random shape and color selection
- Block usage tracking

### `classes/InputHandler.js`
- Mouse event handling
- Touch event handling (with drag support)
- Keyboard controls
- Event listener setup
- Drag-and-drop from preview boxes

### `classes/Renderer.js`
- Canvas drawing operations
- Grid rendering
- Block rendering (placed, dragged, preview)
- Cursor visualization
- Block preview box rendering

### `utils/constants.js`
- Game configuration (grid size, cell size, offsets)
- Color palette
- Scoring multipliers

### `utils/coordinates.js`
- Screen-to-grid coordinate conversion
- Smart snapping algorithm for block placement
- Coordinate scaling for responsive canvas

## Key Features Implemented

1. **Responsive Touch Controls**: Full support for touch dragging with finger offset
2. **Smart Snapping**: Finds nearest valid placement when drag target is invalid
3. **Undo System**: Single-use undo for the last placed block
4. **ES6 Modules**: Clean separation of concerns with modern JavaScript
5. **Canvas Scaling**: Proper coordinate transformation for responsive display
6. **Dynamic Block Library**: 40+ pre-rotated block shapes

## Usage

Include the main script as a module in your HTML:

```html
<script type="module" src="js/main.js"></script>
```

The game will automatically initialize when the DOM is ready and attach to the canvas with ID `gameCanvas`.
