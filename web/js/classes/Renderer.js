// Renderer - Handles all canvas drawing operations
import { GAME_CONFIG, COLORS } from '../utils/constants.js';

export class Renderer {
    constructor(game) {
        this.game = game;
        this.ctx = game.ctx;
        this.canvas = game.canvas;
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = COLORS.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw placed blocks
        this.drawPlacedBlocks();
        
        // Draw cursor only when not dragging
        if (!this.game.isDragging) {
            this.drawCursor();
        }
        
        // Draw block preview - either at cursor or following finger/mouse
        if (this.game.draggedBlock && !this.game.draggedBlock.used && this.game.isDragging) {
            this.drawDraggedBlock();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = COLORS.gridBorder;
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x <= GAME_CONFIG.GRID_SIZE; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(GAME_CONFIG.GRID_OFFSET_X + x * GAME_CONFIG.CELL_SIZE, GAME_CONFIG.GRID_OFFSET_Y);
            this.ctx.lineTo(GAME_CONFIG.GRID_OFFSET_X + x * GAME_CONFIG.CELL_SIZE, GAME_CONFIG.GRID_OFFSET_Y + GAME_CONFIG.GRID_SIZE * GAME_CONFIG.CELL_SIZE);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= GAME_CONFIG.GRID_SIZE; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(GAME_CONFIG.GRID_OFFSET_X, GAME_CONFIG.GRID_OFFSET_Y + y * GAME_CONFIG.CELL_SIZE);
            this.ctx.lineTo(GAME_CONFIG.GRID_OFFSET_X + GAME_CONFIG.GRID_SIZE * GAME_CONFIG.CELL_SIZE, GAME_CONFIG.GRID_OFFSET_Y + y * GAME_CONFIG.CELL_SIZE);
            this.ctx.stroke();
        }
    }
    
    drawPlacedBlocks() {
        // Placed blocks take full cell size
        for (let y = 0; y < GAME_CONFIG.GRID_SIZE; y++) {
            for (let x = 0; x < GAME_CONFIG.GRID_SIZE; x++) {
                if (this.game.grid[y][x] !== 0) {
                    const color = COLORS.blocks[(this.game.grid[y][x] - 1) % COLORS.blocks.length];
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(
                        GAME_CONFIG.GRID_OFFSET_X + x * GAME_CONFIG.CELL_SIZE + 2,
                        GAME_CONFIG.GRID_OFFSET_Y + y * GAME_CONFIG.CELL_SIZE + 2,
                        GAME_CONFIG.CELL_SIZE - 4,
                        GAME_CONFIG.CELL_SIZE - 4
                    );
                }
            }
        }
    }
    
    drawCursor() {
        this.ctx.strokeStyle = COLORS.cursor;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(
            GAME_CONFIG.GRID_OFFSET_X + this.game.cursorPos.x * GAME_CONFIG.CELL_SIZE + 1,
            GAME_CONFIG.GRID_OFFSET_Y + this.game.cursorPos.y * GAME_CONFIG.CELL_SIZE + 1,
            GAME_CONFIG.CELL_SIZE - 2,
            GAME_CONFIG.CELL_SIZE - 2
        );
    }
    
    drawDraggedBlock() {
        const block = this.game.draggedBlock;
        const color = COLORS.blocks[block.colorIndex % COLORS.blocks.length];
        const shapeScale = 0.85; // Scale the entire shape to 85%
        
        // Get the display size vs internal canvas size
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        // Scale the raw mouse position to canvas coordinates
        const scaledX = this.game.rawMousePos.x * scaleX;
        const scaledY = this.game.rawMousePos.y * scaleY;
        
        const cellSize = GAME_CONFIG.CELL_SIZE * shapeScale; // Scale cell size for entire shape
        
        // Calculate block dimensions with scaled cells
        const blockWidth = block.shape[0].length * cellSize;
        const blockHeight = block.shape.length * cellSize;
        
        // Dynamic offset - taller blocks need more offset to stay above finger
        const baseOffset = 80;
        const fingerOffsetY = baseOffset + blockHeight;
        
        // Center the block horizontally on the cursor/finger, offset vertically above it
        const offsetX = scaledX - blockWidth / 2;
        const offsetY = scaledY - blockHeight / 2 - fingerOffsetY;
        
        // Draw the block following the cursor
        this.ctx.fillStyle = color + 'CC'; // More opaque for visibility
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        
        block.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    const x = offsetX + dx * cellSize;
                    const y = offsetY + dy * cellSize;
                    
                    // Draw filled cell with padding
                    this.ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                    
                    // Draw border
                    this.ctx.strokeRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                }
            });
        });
    }
    
    // Draw block preview in the selector boxes
    drawBlockInPreview(block, previewElement, blockIndex) {
        const previewCanvas = previewElement.querySelector('canvas');
        if (!previewCanvas) {
            const canvas = document.createElement('canvas');
            canvas.width = 100;
            canvas.height = 100;
            previewElement.innerHTML = '';
            previewElement.appendChild(canvas);
        }
        
        const canvas = previewElement.querySelector('canvas');
        const ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        if (block && !block.used) {
            const color = COLORS.blocks[block.colorIndex % COLORS.blocks.length];
            const blockWidth = block.shape[0].length;
            const blockHeight = block.shape.length;
            const shapeScale = 0.85; // Scale entire shape to 85%
            
            // Calculate base cell size to fit the canvas
            const baseCellSize = Math.min(
                (canvas.width - 20) / blockWidth,
                (canvas.height - 20) / blockHeight
            );
            
            // Apply scale to the cell size (this creates consistent padding)
            const cellSize = baseCellSize * shapeScale;
            
            // Center the scaled shape
            const totalWidth = blockWidth * cellSize;
            const totalHeight = blockHeight * cellSize;
            const offsetX = (canvas.width - totalWidth) / 2;
            const offsetY = (canvas.height - totalHeight) / 2;
            
            ctx.fillStyle = color;
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1;
            
            block.shape.forEach((row, y) => {
                row.forEach((cell, x) => {
                    if (cell) {
                        ctx.fillRect(
                            offsetX + x * cellSize + 2,
                            offsetY + y * cellSize + 2,
                            cellSize - 4,
                            cellSize - 4
                        );
                        ctx.strokeRect(
                            offsetX + x * cellSize + 2,
                            offsetY + y * cellSize + 2,
                            cellSize - 4,
                            cellSize - 4
                        );
                    }
                });
            });
        }
        
        // Update selection state
        if (this.game.selectedBlockIndex === blockIndex) {
            previewElement.classList.add('selected');
        } else {
            previewElement.classList.remove('selected');
        }
        
        // Dim used blocks
        if (block && block.used) {
            previewElement.style.opacity = '0.3';
        } else {
            previewElement.style.opacity = '1';
        }
    }
}