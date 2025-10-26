// Block Whacker - Web Edition Game Engine
// Complete HTML5/JavaScript conversion with touch controls

class BlockWhackerGame {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Game configuration
        this.GRID_SIZE = 10;
        this.CELL_SIZE = 40;
        this.GRID_OFFSET_X = 50;
        this.GRID_OFFSET_Y = 50;
        
        // Colors
        this.COLORS = {
            background: '#1a1a2e',
            grid: '#16213e',
            gridBorder: '#0f3460',
            cursor: '#ffff00',
            text: '#ffffff',
            blocks: [
                '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
                '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'
            ]
        };
        
        // Game state
        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;
        this.grid = Array(this.GRID_SIZE).fill().map(() => Array(this.GRID_SIZE).fill(0));
        this.selectedBlock = null;
        this.selectedBlockIndex = -1;
        this.availableBlocks = [];
        this.cursorPos = {x: 0, y: 0};
        this.isPaused = false;
        this.gameOver = false;
        
        // Touch/mouse handling
        this.touchStart = null;
        this.isDragging = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.generateNewBlocks();
        this.gameLoop();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Touch events for mobile
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e), {passive: false});
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e), {passive: false});
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e), {passive: false});
        
        // Mouse events for desktop
        this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        
        // Block selection
        document.querySelectorAll('.block-preview').forEach((preview, index) => {
            preview.addEventListener('click', () => this.selectBlock(index));
            preview.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.selectBlock(index);
            });
        });
        
        // Control buttons
        document.getElementById('rotateBtn').addEventListener('click', () => this.rotateBlock());
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetGame());
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Prevent context menu on long press
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    handleTouchStart(e) {
        e.preventDefault();
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        this.touchStart = {x, y};
        this.handlePointerDown(x, y);
    }
    
    handleTouchMove(e) {
        e.preventDefault();
        if (!this.touchStart) return;
        
        const touch = e.touches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        this.handlePointerMove(x, y);
    }
    
    handleTouchEnd(e) {
        e.preventDefault();
        if (!this.touchStart) return;
        
        const touch = e.changedTouches[0];
        const rect = this.canvas.getBoundingClientRect();
        const x = touch.clientX - rect.left;
        const y = touch.clientY - rect.top;
        
        this.handlePointerUp(x, y);
        this.touchStart = null;
    }
    
    handleMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.handlePointerDown(x, y);
    }
    
    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.handlePointerMove(x, y);
    }
    
    handleMouseUp(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        this.handlePointerUp(x, y);
    }
    
    handlePointerDown(x, y) {
        const gridPos = this.screenToGrid(x, y);
        if (gridPos) {
            this.cursorPos = gridPos;
            this.isDragging = true;
        }
    }
    
    handlePointerMove(x, y) {
        if (!this.isDragging) return;
        
        const gridPos = this.screenToGrid(x, y);
        if (gridPos) {
            this.cursorPos = gridPos;
        }
    }
    
    handlePointerUp(x, y) {
        if (this.isDragging && this.selectedBlock) {
            this.placeBlock();
        }
        this.isDragging = false;
    }
    
    handleKeyDown(e) {
        switch(e.key) {
            case 'ArrowUp':
                e.preventDefault();
                this.moveCursor(0, -1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.moveCursor(0, 1);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.moveCursor(-1, 0);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.moveCursor(1, 0);
                break;
            case ' ':
                e.preventDefault();
                this.placeBlock();
                break;
            case 'r':
            case 'R':
                e.preventDefault();
                this.rotateBlock();
                break;
            case '1':
                this.selectBlock(0);
                break;
            case '2':
                this.selectBlock(1);
                break;
            case '3':
                this.selectBlock(2);
                break;
            case 'p':
            case 'P':
                this.togglePause();
                break;
        }
    }
    
    screenToGrid(x, y) {
        const gridX = Math.floor((x - this.GRID_OFFSET_X) / this.CELL_SIZE);
        const gridY = Math.floor((y - this.GRID_OFFSET_Y) / this.CELL_SIZE);
        
        if (gridX >= 0 && gridX < this.GRID_SIZE && gridY >= 0 && gridY < this.GRID_SIZE) {
            return {x: gridX, y: gridY};
        }
        return null;
    }
    
    moveCursor(dx, dy) {
        this.cursorPos.x = Math.max(0, Math.min(this.GRID_SIZE - 1, this.cursorPos.x + dx));
        this.cursorPos.y = Math.max(0, Math.min(this.GRID_SIZE - 1, this.cursorPos.y + dy));
    }
    
    selectBlock(index) {
        if (index >= 0 && index < this.availableBlocks.length && !this.availableBlocks[index].used) {
            this.selectedBlock = this.availableBlocks[index];
            this.selectedBlockIndex = index;
            this.updateBlockPreviews();
        }
    }
    
    rotateBlock() {
        if (this.selectedBlock) {
            this.selectedBlock.rotate();
        }
    }
    
    placeBlock() {
        if (!this.selectedBlock || this.selectedBlock.used) return;
        
        if (this.canPlaceBlock(this.selectedBlock, this.cursorPos)) {
            // Place the block
            this.selectedBlock.shape.forEach((row, dy) => {
                row.forEach((cell, dx) => {
                    if (cell) {
                        const x = this.cursorPos.x + dx;
                        const y = this.cursorPos.y + dy;
                        if (x >= 0 && x < this.GRID_SIZE && y >= 0 && y < this.GRID_SIZE) {
                            this.grid[y][x] = this.selectedBlock.colorIndex;
                        }
                    }
                });
            });
            
            // Mark block as used
            this.selectedBlock.used = true;
            this.selectedBlock = null;
            this.selectedBlockIndex = -1;
            
            // Check for line clears
            this.checkAndClearLines();
            
            // Generate new blocks if all are used
            if (this.availableBlocks.every(block => block.used)) {
                this.generateNewBlocks();
            }
            
            this.updateBlockPreviews();
            this.updateUI();
        }
    }
    
    canPlaceBlock(block, pos) {
        return block.shape.every((row, dy) => {
            return row.every((cell, dx) => {
                if (!cell) return true;
                
                const x = pos.x + dx;
                const y = pos.y + dy;
                
                return x >= 0 && x < this.GRID_SIZE && 
                       y >= 0 && y < this.GRID_SIZE && 
                       this.grid[y][x] === 0;
            });
        });
    }
    
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
        const baseScore = 100;
        let multiplier;
        
        switch(linesCleared) {
            case 1: multiplier = 1; break;
            case 2: multiplier = 3; break;
            case 3: multiplier = 6; break;
            default: multiplier = 10; break;
        }
        
        this.score += baseScore * multiplier;
        this.level = Math.floor(this.linesCleared / 10) + 1;
    }
    
    generateNewBlocks() {
        this.availableBlocks = [];
        
        for (let i = 0; i < 3; i++) {
            this.availableBlocks.push(new Block());
        }
        
        this.updateBlockPreviews();
    }
    
    updateBlockPreviews() {
        const previews = document.querySelectorAll('.block-preview');
        previews.forEach((preview, index) => {
            preview.classList.toggle('selected', index === this.selectedBlockIndex);
            
            if (this.availableBlocks[index]) {
                preview.style.opacity = this.availableBlocks[index].used ? '0.3' : '1';
                preview.textContent = (index + 1).toString();
                preview.style.backgroundColor = this.availableBlocks[index].used ? 
                    'rgba(100,100,100,0.2)' : 
                    this.COLORS.blocks[this.availableBlocks[index].colorIndex % this.COLORS.blocks.length] + '40';
            }
        });
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        document.getElementById('pauseBtn').textContent = this.isPaused ? '▶️ Resume' : '⏸️ Pause';
    }
    
    resetGame() {
        this.score = 0;
        this.level = 1;
        this.linesCleared = 0;
        this.grid = Array(this.GRID_SIZE).fill().map(() => Array(this.GRID_SIZE).fill(0));
        this.selectedBlock = null;
        this.selectedBlockIndex = -1;
        this.cursorPos = {x: 0, y: 0};
        this.isPaused = false;
        this.gameOver = false;
        
        this.generateNewBlocks();
        this.updateUI();
        document.getElementById('pauseBtn').textContent = '⏸️ Pause';
    }
    
    updateUI() {
        document.getElementById('score').textContent = `Score: ${this.score}`;
        document.querySelector('#gameInfo div:nth-child(1)').textContent = `Level: ${this.level}`;
        document.querySelector('#gameInfo div:nth-child(2)').textContent = `Lines: ${this.linesCleared}`;
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = this.COLORS.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid
        this.drawGrid();
        
        // Draw placed blocks
        this.drawPlacedBlocks();
        
        // Draw cursor
        this.drawCursor();
        
        // Draw block preview at cursor
        if (this.selectedBlock && !this.selectedBlock.used) {
            this.drawBlockPreview();
        }
        
        // Draw pause overlay
        if (this.isPaused) {
            this.drawPauseOverlay();
        }
    }
    
    drawGrid() {
        this.ctx.strokeStyle = this.COLORS.gridBorder;
        this.ctx.lineWidth = 1;
        
        for (let x = 0; x <= this.GRID_SIZE; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(this.GRID_OFFSET_X + x * this.CELL_SIZE, this.GRID_OFFSET_Y);
            this.ctx.lineTo(this.GRID_OFFSET_X + x * this.CELL_SIZE, this.GRID_OFFSET_Y + this.GRID_SIZE * this.CELL_SIZE);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= this.GRID_SIZE; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(this.GRID_OFFSET_X, this.GRID_OFFSET_Y + y * this.CELL_SIZE);
            this.ctx.lineTo(this.GRID_OFFSET_X + this.GRID_SIZE * this.CELL_SIZE, this.GRID_OFFSET_Y + y * this.CELL_SIZE);
            this.ctx.stroke();
        }
    }
    
    drawPlacedBlocks() {
        for (let y = 0; y < this.GRID_SIZE; y++) {
            for (let x = 0; x < this.GRID_SIZE; x++) {
                if (this.grid[y][x] !== 0) {
                    const color = this.COLORS.blocks[(this.grid[y][x] - 1) % this.COLORS.blocks.length];
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(
                        this.GRID_OFFSET_X + x * this.CELL_SIZE + 2,
                        this.GRID_OFFSET_Y + y * this.CELL_SIZE + 2,
                        this.CELL_SIZE - 4,
                        this.CELL_SIZE - 4
                    );
                }
            }
        }
    }
    
    drawCursor() {
        this.ctx.strokeStyle = this.COLORS.cursor;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(
            this.GRID_OFFSET_X + this.cursorPos.x * this.CELL_SIZE + 1,
            this.GRID_OFFSET_Y + this.cursorPos.y * this.CELL_SIZE + 1,
            this.CELL_SIZE - 2,
            this.CELL_SIZE - 2
        );
    }
    
    drawBlockPreview() {
        const block = this.selectedBlock;
        const color = this.COLORS.blocks[block.colorIndex % this.COLORS.blocks.length];
        
        this.ctx.fillStyle = color + '80'; // Semi-transparent
        
        block.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    const x = this.cursorPos.x + dx;
                    const y = this.cursorPos.y + dy;
                    
                    if (x >= 0 && x < this.GRID_SIZE && y >= 0 && y < this.GRID_SIZE) {
                        this.ctx.fillRect(
                            this.GRID_OFFSET_X + x * this.CELL_SIZE + 2,
                            this.GRID_OFFSET_Y + y * this.CELL_SIZE + 2,
                            this.CELL_SIZE - 4,
                            this.CELL_SIZE - 4
                        );
                    }
                }
            });
        });
    }
    
    drawPauseOverlay() {
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = this.COLORS.text;
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('PAUSED', this.canvas.width / 2, this.canvas.height / 2);
    }
    
    gameLoop() {
        if (!this.isPaused) {
            this.draw();
        }
        requestAnimationFrame(() => this.gameLoop());
    }
}

// Block class
class Block {
    constructor() {
        this.shapes = [
            // Single block
            [[1]],
            
            // Line blocks
            [[1, 1]],
            [[1], [1]],
            [[1, 1, 1]],
            [[1], [1], [1]],
            
            // L shapes
            [[1, 1], [1, 0]],
            [[1, 0], [1, 1]],
            [[1, 1], [0, 1]],
            [[0, 1], [1, 1]],
            
            // Square
            [[1, 1], [1, 1]],
            
            // T shapes
            [[1, 1, 1], [0, 1, 0]],
            [[1, 0], [1, 1], [1, 0]],
            [[0, 1, 0], [1, 1, 1]],
            [[0, 1], [1, 1], [0, 1]],
            
            // Big L
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1, 1], [0, 0, 1]],
            [[1, 0, 0], [1, 1, 1]],
            [[0, 0, 1], [1, 1, 1]]
        ];
        
        this.shape = this.shapes[Math.floor(Math.random() * this.shapes.length)];
        this.colorIndex = Math.floor(Math.random() * 8) + 1;
        this.used = false;
    }
    
    rotate() {
        // Rotate 90 degrees clockwise
        const rows = this.shape.length;
        const cols = this.shape[0].length;
        const rotated = Array(cols).fill().map(() => Array(rows).fill(0));
        
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                rotated[x][rows - 1 - y] = this.shape[y][x];
            }
        }
        
        this.shape = rotated;
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new BlockWhackerGame('gameCanvas');
});