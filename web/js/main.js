// Main entry point for Block Whacker game
import { BlockWhackerGame } from './classes/Game.js';

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new BlockWhackerGame('gameCanvas');
});
