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
        const blockScale = 0.9; // Blocks are 90% of cell size
        const offset = (GAME_CONFIG.CELL_SIZE * (1 - blockScale)) / 2;
        
        for (let y = 0; y < GAME_CONFIG.GRID_SIZE; y++) {
            for (let x = 0; x < GAME_CONFIG.GRID_SIZE; x++) {
                if (this.game.grid[y][x] !== 0) {
                    const color = COLORS.blocks[(this.game.grid[y][x] - 1) % COLORS.blocks.length];
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(
                        GAME_CONFIG.GRID_OFFSET_X + x * GAME_CONFIG.CELL_SIZE + offset,
                        GAME_CONFIG.GRID_OFFSET_Y + y * GAME_CONFIG.CELL_SIZE + offset,
                        GAME_CONFIG.CELL_SIZE * blockScale,
                        GAME_CONFIG.CELL_SIZE * blockScale
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
        const blockScale = 0.9; // Blocks are 90% of cell size
        const offset = (GAME_CONFIG.CELL_SIZE * (1 - blockScale)) / 2;
        
        // Get the display size vs internal canvas size
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        // Scale the raw mouse position to canvas coordinates
        const scaledX = this.game.rawMousePos.x * scaleX;
        const scaledY = this.game.rawMousePos.y * scaleY;
        
        const cellSize = GAME_CONFIG.CELL_SIZE;
        
        // Calculate block dimensions
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
                    const x = offsetX + dx * cellSize + offset;
                    const y = offsetY + dy * cellSize + offset;
                    
                    // Draw filled cell
                    this.ctx.fillRect(x, y, cellSize * blockScale, cellSize * blockScale);
                    
                    // Draw border
                    this.ctx.strokeRect(x, y, cellSize * blockScale, cellSize * blockScale);
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
            const cellSize = Math.min(
                (canvas.width - 20) / blockWidth,
                (canvas.height - 20) / blockHeight
            );
            const blockScale = 0.9; // Blocks are 90% of cell size
            const offset = (cellSize * (1 - blockScale)) / 2;
            
            const offsetX = (canvas.width - blockWidth * cellSize) / 2;
            const offsetY = (canvas.height - blockHeight * cellSize) / 2;
            
            ctx.fillStyle = color;
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1;
            
            block.shape.forEach((row, y) => {
                row.forEach((cell, x) => {
                    if (cell) {
                        ctx.fillRect(
                            offsetX + x * cellSize + offset,
                            offsetY + y * cellSize + offset,
                            cellSize * blockScale,
                            cellSize * blockScale
                        );
                        ctx.strokeRect(
                            offsetX + x * cellSize + offset,
                            offsetY + y * cellSize + offset,
                            cellSize * blockScale,
                            cellSize * blockScale
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
