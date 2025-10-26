// Game Logic Utilities - Move validation and game state checks
import { GAME_CONFIG } from './constants.js';

/**
 * Check if any of the available blocks can be placed anywhere on the grid
 */
export function hasAnyValidMoves(grid, availableBlocks) {
    // Filter out used blocks
    const activeBlocks = availableBlocks.filter(block => !block.used);
    
    if (activeBlocks.length === 0) {
        return true; // Will generate new blocks, not game over
    }
    
    // Check if any block can fit anywhere
    for (const block of activeBlocks) {
        for (let y = 0; y < GAME_CONFIG.GRID_SIZE; y++) {
            for (let x = 0; x < GAME_CONFIG.GRID_SIZE; x++) {
                if (canPlaceBlockAt(grid, block, {x, y})) {
                    return true;
                }
            }
        }
    }
    
    return false; // No valid moves!
}

/**
 * Check if a specific block can be placed at a position
 */
export function canPlaceBlockAt(grid, block, pos) {
    if (!block || !block.shape) return false;
    
    for (let y = 0; y < block.shape.length; y++) {
        for (let x = 0; x < block.shape[y].length; x++) {
            if (block.shape[y][x]) {
                const gridX = pos.x + x;
                const gridY = pos.y + y;
                
                if (gridX < 0 || gridX >= GAME_CONFIG.GRID_SIZE || 
                    gridY < 0 || gridY >= GAME_CONFIG.GRID_SIZE ||
                    grid[gridY][gridX] !== 0) {
                    return false;
                }
            }
        }
    }
    return true;
}

/**
 * Find all valid positions for a block
 */
export function findAllValidPositions(grid, block) {
    const validPositions = [];
    
    for (let y = 0; y < GAME_CONFIG.GRID_SIZE; y++) {
        for (let x = 0; x < GAME_CONFIG.GRID_SIZE; x++) {
            if (canPlaceBlockAt(grid, block, {x, y})) {
                validPositions.push({x, y});
            }
        }
    }
    
    return validPositions;
}

/**
 * Evaluate how good a position is (simple heuristic)
 * Higher score = better position
 */
export function evaluatePosition(grid, block, pos) {
    let score = 0;
    
    // Simulate placement
    const testGrid = grid.map(row => [...row]);
    block.shape.forEach((row, dy) => {
        row.forEach((cell, dx) => {
            if (cell) {
                testGrid[pos.y + dy][pos.x + dx] = block.colorIndex;
            }
        });
    });
    
    // Check how many lines this would complete
    let linesCompleted = 0;
    
    // Check rows
    for (let y = 0; y < GAME_CONFIG.GRID_SIZE; y++) {
        if (testGrid[y].every(cell => cell !== 0)) {
            linesCompleted++;
        }
    }
    
    // Check columns
    for (let x = 0; x < GAME_CONFIG.GRID_SIZE; x++) {
        if (testGrid.every(row => row[x] !== 0)) {
            linesCompleted++;
        }
    }
    
    score += linesCompleted * 100;
    
    // Prefer positions that keep pieces grouped (avoid isolated cells)
    let adjacentCells = 0;
    block.shape.forEach((row, dy) => {
        row.forEach((cell, dx) => {
            if (cell) {
                const px = pos.x + dx;
                const py = pos.y + dy;
                
                // Check adjacent cells
                const directions = [{dx: -1, dy: 0}, {dx: 1, dy: 0}, {dx: 0, dy: -1}, {dx: 0, dy: 1}];
                directions.forEach(dir => {
                    const nx = px + dir.dx;
                    const ny = py + dir.dy;
                    if (nx >= 0 && nx < GAME_CONFIG.GRID_SIZE && 
                        ny >= 0 && ny < GAME_CONFIG.GRID_SIZE && 
                        testGrid[ny][nx] !== 0) {
                        adjacentCells++;
                    }
                });
            }
        });
    });
    
    score += adjacentCells * 5;
    
    // Prefer lower positions (more stable)
    score += pos.y * 2;
    
    return score;
}

/**
 * Find the best position for a block (for hint system)
 */
export function findBestPosition(grid, block) {
    const validPositions = findAllValidPositions(grid, block);
    
    if (validPositions.length === 0) {
        return null;
    }
    
    let bestPos = validPositions[0];
    let bestScore = evaluatePosition(grid, block, bestPos);
    
    for (let i = 1; i < validPositions.length; i++) {
        const score = evaluatePosition(grid, block, validPositions[i]);
        if (score > bestScore) {
            bestScore = score;
            bestPos = validPositions[i];
        }
    }
    
    return { position: bestPos, score: bestScore };
}
