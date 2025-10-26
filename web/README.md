# Block Whacker - Web Edition

A fully functional web version of Block Whacker that runs in browsers with full touch support for mobile devices.

## Features

- **Touch Controls**: Full iPhone/mobile support with touch gestures
- **Responsive Design**: Adapts to different screen sizes
- **Progressive Scoring**: Same scoring system as the original
- **Block Preview**: See where blocks will be placed
- **Keyboard Support**: Full keyboard controls for desktop
- **Mobile Optimized**: Optimized UI for mobile devices

## Controls

### Mobile/Touch
- **Tap**: Select grid position or blocks
- **Drag**: Move cursor around grid
- **Block Numbers (1,2,3)**: Tap to select blocks
- **Rotate Button**: Rotate selected block
- **Pause/Resume**: Game control
- **Reset**: Start new game

### Desktop/Keyboard
- **Arrow Keys**: Move cursor
- **1, 2, 3**: Select blocks
- **R**: Rotate block
- **Space**: Place block
- **P**: Pause/Resume
- **Mouse**: Click to place blocks

## Deployment Options

### Option 1: Static Hosting (Recommended)
Deploy to any static hosting service:

- **GitHub Pages**: Enable in repository settings
- **Netlify**: Drag and drop the `web` folder
- **Vercel**: Connect to GitHub repository
- **Firebase Hosting**: `firebase deploy`

### Option 2: Convert Python Version
Use pygbag to convert the Python version:

```bash
pip install pygbag
pygbag main_modular.py
```

### Option 3: Progressive Web App (PWA)
Add a manifest.json and service worker for installable web app.

## Files

- `index.html` - Main game page
- `game.js` - Complete game engine
- `manifest.json` - PWA configuration (optional)
- `sw.js` - Service worker (optional)

## iPhone Compatibility

The web version is optimized for iPhone with:
- Touch-friendly controls
- Proper viewport settings
- Responsive layout
- Gesture prevention to avoid conflicts
- Optimized button sizes for touch

## Live Demo

Once deployed, the game will be accessible at your chosen URL and will work seamlessly on iPhone browsers (Safari, Chrome, etc.).