// Main Game Class - Block Whacker Game Engine
import { GAME_CONFIG, COLORS, SCORING } from '../utils/constants.js';
import { screenToGrid, findNearestValidPosition } from '../utils/coordinates.js';
import { hasAnyValidMoves } from '../utils/gameLogic.js';
import { Block } from './Block.js';
import { Renderer } from './Renderer.js';
import { InputHandler } from './InputHandler.js';
import { EffectsManager } from './EffectsManager.js';

export class BlockWhackerGame {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Game configuration (from constants)
        this.GRID_SIZE = GAME_CONFIG.GRID_SIZE;
        this.CELL_SIZE = GAME_CONFIG.CELL_SIZE;
        this.GRID_OFFSET_X = GAME_CONFIG.GRID_OFFSET_X;
        this.GRID_OFFSET_Y = GAME_CONFIG.GRID_OFFSET_Y;
        this.COLORS = COLORS;
        
        // Game state
        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;
        this.grid = Array(this.GRID_SIZE).fill().map(() => Array(this.GRID_SIZE).fill(0));
        this.selectedBlock = null;
        this.selectedBlockIndex = -1;
        this.availableBlocks = [];
        this.cursorPos = {x: 0, y: 0};
        this.gameOver = false;
        
        // Touch/mouse handling
        this.touchStart = null;
        this.isDragging = false;
        this.draggedBlock = null;
        this.dragOffset = {x: 0, y: 0};
        this.mousePos = {x: 0, y: 0};
        this.rawMousePos = {x: 0, y: 0};
        
        // Undo functionality
        this.lastPlacement = null;
        this.canUndo = false;
        
        // Timing for animations
        this.lastFrameTime = performance.now();
        
        // Initialize subsystems
        this.renderer = new Renderer(this);
        this.inputHandler = new InputHandler(this);
        this.effectsManager = new EffectsManager(this);
        
        this.init();
    }
    
    init() {
        this.generateNewBlocks();
        this.updateUndoButton();
        this.gameLoop();
        this.updateUI();
    }
    
    // ============ COORDINATE & CURSOR METHODS ============
    
    screenToGrid(x, y) {
        return screenToGrid(this.canvas, x, y);
    }
    
    moveCursor(dx, dy) {
        this.cursorPos.x = Math.max(0, Math.min(this.GRID_SIZE - 1, this.cursorPos.x + dx));
        this.cursorPos.y = Math.max(0, Math.min(this.GRID_SIZE - 1, this.cursorPos.y + dy));
    }
    
    updateCursorFromMouse() {
        if (this.isDragging && this.draggedBlock) {
            const rect = this.canvas.getBoundingClientRect();
            const scaleX = this.canvas.width / rect.width;
            const scaleY = this.canvas.height / rect.height;
            
            const scaledX = this.rawMousePos.x * scaleX;
            const scaledY = this.rawMousePos.y * scaleY;
            
            const cellSize = this.CELL_SIZE;
            const blockWidth = this.draggedBlock.shape[0].length * cellSize;
            const blockHeight = this.draggedBlock.shape.length * cellSize;
            
            const baseOffset = 80;
            const fingerOffsetY = baseOffset + blockHeight;
            const offsetX = scaledX - blockWidth / 2;
            const offsetY = scaledY - blockHeight / 2 - fingerOffsetY;
            
            const blockCenterX = offsetX + blockWidth / 2;
            const blockCenterY = offsetY + blockHeight / 2;
            
            const screenCenterX = blockCenterX / scaleX;
            const screenCenterY = blockCenterY / scaleY;
            const gridPos = this.screenToGrid(screenCenterX, screenCenterY);
            
            if (gridPos) {
                if (this.canPlaceBlock(this.draggedBlock, gridPos)) {
                    this.cursorPos = gridPos;
                } else {
                    const nearest = findNearestValidPosition(
                        this.draggedBlock, 
                        gridPos, 
                        (block, pos) => this.canPlaceBlock(block, pos)
                    );
                    if (nearest) {
                        this.cursorPos = nearest;
                    }
                }
            }
        } else {
            const gridPos = this.screenToGrid(this.rawMousePos.x, this.rawMousePos.y);
            if (gridPos) {
                this.cursorPos = gridPos;
            }
        }
    }
    
    // ============ BLOCK MANAGEMENT ============
    
    selectBlock(index) {
        if (index >= 0 && index < this.availableBlocks.length && !this.availableBlocks[index].used) {
            this.selectedBlock = this.availableBlocks[index];
            this.selectedBlockIndex = index;
            this.draggedBlock = this.selectedBlock;
            this.updateBlockPreviews();
        }
    }
    
    generateNewBlocks() {
        this.availableBlocks = [new Block(), new Block(), new Block()];
        this.updateBlockPreviews();
    }
    
    updateBlockPreviews() {
        document.querySelectorAll('.block-preview').forEach((preview, index) => {
            const block = this.availableBlocks[index];
            if (block) {
                this.renderer.drawBlockInPreview(block, preview, index);
            }
        });
    }
    
    // ============ PLACEMENT & VALIDATION ============
    
    canPlaceBlock(block, pos) {
        if (!block) return false;
        
        for (let y = 0; y < block.shape.length; y++) {
            for (let x = 0; x < block.shape[y].length; x++) {
                if (block.shape[y][x]) {
                    const gridX = pos.x + x;
                    const gridY = pos.y + y;
                    
                    if (gridX < 0 || gridX >= this.GRID_SIZE || 
                        gridY < 0 || gridY >= this.GRID_SIZE ||
                        this.grid[gridY][gridX] !== 0) {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    
    tryPlaceBlock() {
        if (this.draggedBlock && this.canPlaceBlock(this.draggedBlock, this.cursorPos)) {
            this.placeBlock();
        }
    }
    
    placeBlock() {
        if (!this.draggedBlock || this.draggedBlock.used) return;
        
        if (this.canPlaceBlock(this.draggedBlock, this.cursorPos)) {
            // Save state for undo
            this.lastPlacement = {
                grid: this.grid.map(row => [...row]),
                block: this.draggedBlock,
                blockIndex: this.selectedBlockIndex,
                position: {...this.cursorPos},
                score: this.score,
                linesCleared: this.linesCleared
            };
            this.canUndo = true;
            this.updateUndoButton();
            
            // Place the block
            this.draggedBlock.shape.forEach((row, dy) => {
                row.forEach((cell, dx) => {
                    if (cell) {
                        const x = this.cursorPos.x + dx;
                        const y = this.cursorPos.y + dy;
                        if (x >= 0 && x < this.GRID_SIZE && y >= 0 && y < this.GRID_SIZE) {
                            this.grid[y][x] = this.draggedBlock.colorIndex;
                        }
                    }
                });
            });
            
            // Create placement effect
            this.effectsManager.createBlockPlacementEffect(this.draggedBlock, this.cursorPos);
            
            // Mark block as used
            this.draggedBlock.used = true;
            this.selectedBlock = null;
            this.selectedBlockIndex = -1;
            
            // Check for line clears
            this.checkAndClearLines();
            
            // Generate new blocks if all are used
            if (this.availableBlocks.every(block => block.used)) {
                this.generateNewBlocks();
            }
            
            // Check for game over
            this.checkGameOver();
            
            this.updateBlockPreviews();
            this.updateUI();
        }
    }
    
    // ============ UNDO ============
    
    undo() {
        if (!this.canUndo || !this.lastPlacement) return;
        
        this.grid = this.lastPlacement.grid;
        this.lastPlacement.block.used = false;
        this.score = this.lastPlacement.score;
        this.linesCleared = this.lastPlacement.linesCleared;
        
        this.canUndo = false;
        this.updateUndoButton();
        
        this.updateBlockPreviews();
        this.updateUI();
    }
    
    updateUndoButton() {
        const undoBtn = document.getElementById('undoBtn');
        if (this.canUndo) {
            undoBtn.style.opacity = '1';
            undoBtn.style.cursor = 'pointer';
        } else {
            undoBtn.style.opacity = '0.5';
            undoBtn.style.cursor = 'not-allowed';
        }
    }
    
    // ============ SCORING & LINE CLEARING ============
    
    checkAndClearLines() {
        let linesCleared = 0;
        let clearedRows = [];
        let clearedCols = [];
        
        // Check rows
        for (let y = 0; y < this.GRID_SIZE; y++) {
            if (this.grid[y].every(cell => cell !== 0)) {
                clearedRows.push(y);
                linesCleared++;
            }
        }
        
        // Check columns
        for (let x = 0; x < this.GRID_SIZE; x++) {
            if (this.grid.every(row => row[x] !== 0)) {
                clearedCols.push(x);
                linesCleared++;
            }
        }
        
        // Create visual effects BEFORE clearing
        if (linesCleared > 0) {
            this.effectsManager.createLineClearEffect(clearedRows, clearedCols);
        }
        
        // Clear the lines
        clearedRows.forEach(y => {
            this.grid[y].fill(0);
        });
        
        clearedCols.forEach(x => {
            this.grid.forEach(row => {
                row[x] = 0;
            });
        });
        
        // Update score
        if (linesCleared > 0) {
            this.updateScore(linesCleared);
            this.linesCleared += linesCleared;
        }
    }
    
    updateScore(linesCleared) {
        const baseScore = SCORING.BASE_SCORE;
        const multiplier = SCORING.MULTIPLIERS[linesCleared] || SCORING.MULTIPLIERS.default;
        this.score += baseScore * multiplier * this.level;
    }
    
    // ============ GAME OVER & VALIDATION ============
    
    checkGameOver() {
        if (!hasAnyValidMoves(this.grid, this.availableBlocks)) {
            this.gameOver = true;
            this.effectsManager.createIconTextPopup(
                'skull',
                'GAME OVER!',
                this.canvas.width / 2,
                this.canvas.height / 2,
                true
            );
            
            // Show final score
            setTimeout(() => {
                this.effectsManager.createTextPopup(
                    `Final Score: ${this.score}`,
                    this.canvas.width / 2,
                    this.canvas.height / 2 + 80,
                    false
                );
            }, 500);
        }
    }
    
    // ============ UI & GAME CONTROL ============
    
    resetGame() {
        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;
        this.grid = Array(this.GRID_SIZE).fill().map(() => Array(this.GRID_SIZE).fill(0));
        this.selectedBlock = null;
        this.selectedBlockIndex = -1;
        this.cursorPos = {x: 0, y: 0};
        this.gameOver = false;
        
        // Reset undo state
        this.lastPlacement = null;
        this.canUndo = false;
        this.updateUndoButton();
        
        // Clear effects
        this.effectsManager.particles = [];
        this.effectsManager.textPopups = [];
        this.effectsManager.iconPopups = [];
        
        this.generateNewBlocks();
        this.updateUI();
    }
    
    updateUI() {
        document.getElementById('score').textContent = `Score: ${this.score}`;
        document.querySelector('#gameInfo div:nth-child(1)').textContent = `Level: ${this.level}`;
        document.querySelector('#gameInfo div:nth-child(2)').textContent = `Lines: ${this.linesCleared}`;
    }
    
    // ============ GAME LOOP ============
    
    draw() {
        // Calculate delta time
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        this.lastFrameTime = currentTime;
        
        // Update effects
        this.effectsManager.update(deltaTime / 16); // Normalize to 60fps baseline
        
        // Draw everything
        this.renderer.draw();
        this.effectsManager.draw();
    }
    
    gameLoop() {
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
}
