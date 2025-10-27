// Coordinate transformation utilities
import { GAME_CONFIG } from './constants.js';

/**
 * Convert screen coordinates to grid coordinates (top-left cell)
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
 * Convert screen coordinates to exact grid position (with fractional parts)
 * Returns the center of the block shape in grid coordinates
 */
export function screenToGridExact(canvas, block, screenX, screenY) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const scaledX = screenX * scaleX;
    const scaledY = screenY * scaleY;
    
    // Calculate block dimensions (full size)
    const cellSize = GAME_CONFIG.CELL_SIZE;
    const blockWidth = block.shape[0].length * cellSize;
    const blockHeight = block.shape.length * cellSize;
    
    // Find top-left corner of the block (accounting for finger offset)
    const baseOffset = 80;
    const fingerOffsetY = baseOffset + blockHeight;
    
    const blockLeft = scaledX - blockWidth / 2;
    const blockTop = scaledY - blockHeight / 2 - fingerOffsetY;
    
    // Convert to grid coordinates
    const gridX = (blockLeft - GAME_CONFIG.GRID_OFFSET_X) / GAME_CONFIG.CELL_SIZE;
    const gridY = (blockTop - GAME_CONFIG.GRID_OFFSET_Y) / GAME_CONFIG.CELL_SIZE;
    
    return { x: gridX, y: gridY };
}

/**
 * Find best grid position based on maximum overlap with grid cells
 */
export function findBestOverlapPosition(canvas, block, screenX, screenY, canPlaceBlockFn) {
    // Get exact position of block center in grid coordinates
    const exactPos = screenToGridExact(canvas, block, screenX, screenY);
    if (!exactPos) return null;
    
    // Get the block's shape dimensions
    const blockWidth = block.shape[0].length;
    const blockHeight = block.shape.length;
    
    // Calculate which grid positions the block overlaps
    // We'll check a range around where the block visually appears
    const startX = Math.floor(exactPos.x);
    const startY = Math.floor(exactPos.y);
    
    let bestPosition = null;
    let maxOverlap = 0;
    let bestDistance = Infinity;
    
    // Check all nearby grid positions
    for (let testY = startY - 1; testY <= startY + 1; testY++) {
        for (let testX = startX - 1; testX <= startX + 1; testX++) {
            const testPos = { x: testX, y: testY };
            
            // Check if this position is valid
            if (!canPlaceBlockFn(block, testPos)) continue;
            
            // Calculate overlap score for this position
            let overlapScore = 0;
            
            // For each filled cell in the block shape
            for (let by = 0; by < blockHeight; by++) {
                for (let bx = 0; bx < blockWidth; bx++) {
                    if (!block.shape[by][bx]) continue;
                    
                    // Where is this cell's CENTER in grid coordinates?
                    const cellCenterGridX = exactPos.x + bx + 0.5;
                    const cellCenterGridY = exactPos.y + by + 0.5;
                    
                    // Where would this cell be if placed at testPos?
                    const targetCenterGridX = testPos.x + bx + 0.5;
                    const targetCenterGridY = testPos.y + by + 0.5;
                    
                    // Calculate how close the centers are (closer = better overlap)
                    const distX = Math.abs(cellCenterGridX - targetCenterGridX);
                    const distY = Math.abs(cellCenterGridY - targetCenterGridY);
                    
                    // Convert distance to overlap score (0.0 at distance 1.0, 1.0 at distance 0.0)
                    const overlapX = Math.max(0, 1 - distX);
                    const overlapY = Math.max(0, 1 - distY);
                    const cellOverlap = overlapX * overlapY;
                    
                    overlapScore += cellOverlap;
                }
            }
            
            // Calculate distance from exact position (for tiebreaking)
            const dx = testPos.x - exactPos.x;
            const dy = testPos.y - exactPos.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            // Update best position if this one has better overlap, or same overlap but closer
            if (overlapScore > maxOverlap || (overlapScore === maxOverlap && distance < bestDistance)) {
                maxOverlap = overlapScore;
                bestDistance = distance;
                bestPosition = testPos;
            }
        }
    }
    
    return bestPosition;
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
