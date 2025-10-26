// Coordinate transformation utilities
import { GAME_CONFIG } from './constants.js';

/**
 * Convert screen coordinates to grid coordinates
 */
export function screenToGrid(canvas, screenX, screenY) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const scaledX = screenX * scaleX;
    const scaledY = screenY * scaleY;
    
    const gridX = Math.floor((scaledX - GAME_CONFIG.GRID_OFFSET_X) / GAME_CONFIG.CELL_SIZE);
    const gridY = Math.floor((scaledY - GAME_CONFIG.GRID_OFFSET_Y) / GAME_CONFIG.CELL_SIZE);
    
    if (gridX >= 0 && gridX < GAME_CONFIG.GRID_SIZE && 
        gridY >= 0 && gridY < GAME_CONFIG.GRID_SIZE) {
        return { x: gridX, y: gridY };
    }
    return null;
}

/**
 * Find the nearest valid position for a block placement
 */
export function findNearestValidPosition(block, targetPos, canPlaceBlockFn) {
    const maxDistance = 3; // Search within 3 cells
    
    for (let distance = 1; distance <= maxDistance; distance++) {
        let bestPos = null;
        let bestDist = Infinity;
        
        // Check all positions at this distance
        for (let dy = -distance; dy <= distance; dy++) {
            for (let dx = -distance; dx <= distance; dx++) {
                // Only check positions at exactly this distance (Manhattan distance)
                if (Math.abs(dx) + Math.abs(dy) !== distance) continue;
                
                const testPos = {
                    x: targetPos.x + dx,
                    y: targetPos.y + dy
                };
                
                // Check if this position is valid
                if (canPlaceBlockFn(block, testPos)) {
                    // Calculate Euclidean distance - pick the truly closest position
                    const dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < bestDist) {
                        bestDist = dist;
                        bestPos = testPos;
                    }
                }
            }
        }
        
        // Return the first valid position we find
        if (bestPos) return bestPos;
    }
    
    return null; // No valid position found within search range
}
