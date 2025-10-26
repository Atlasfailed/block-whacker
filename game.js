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
        this.draggedBlock = null;
        this.dragOffset = {x: 0, y: 0};
        this.mousePos = {x: 0, y: 0};
        this.rawMousePos = {x: 0, y: 0}; // Actual screen position for drawing
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.generateNewBlocks();
        this.gameLoop();
        this.updateUI();
    }
    
    setupEventListeners() {
        // Canvas mouse/touch events for dragging
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleCanvasTouchMove(e), {passive: false});
        this.canvas.addEventListener('touchend', (e) => this.handleCanvasTouchEnd(e), {passive: false});
        
        // Global mouse/touch events for dragging outside canvas
        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.handleCanvasMouseMove(e);
            }
        });
        document.addEventListener('mouseup', (e) => {
            if (this.isDragging) {
                this.handleCanvasMouseUp(e);
            }
        });
        document.addEventListener('touchmove', (e) => {
            if (this.isDragging) {
                this.handleCanvasTouchMove(e);
            }
        }, {passive: false});
        document.addEventListener('touchend', (e) => {
            if (this.isDragging) {
                this.handleCanvasTouchEnd(e);
            }
        }, {passive: false});
        
        // Block preview dragging
        document.querySelectorAll('.block-preview').forEach((preview, index) => {
            // Mouse events
            preview.addEventListener('mousedown', (e) => this.startDragFromPreview(e, index));
            
            // Touch events
            preview.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.startDragFromPreview(e, index);
            }, {passive: false});
        });
        
        // Control buttons
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetGame());
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Prevent context menu on long press
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    startDragFromPreview(e, index) {
        if (this.availableBlocks[index] && !this.availableBlocks[index].used) {
            this.draggedBlock = this.availableBlocks[index];
            this.selectedBlockIndex = index;
            this.isDragging = true;
            
            // Get initial position - the touch is on the preview box, not the canvas
            const rect = this.canvas.getBoundingClientRect();
            if (e.type === 'mousedown') {
                this.mousePos = {x: e.clientX, y: e.clientY};
                // Convert screen position to canvas-relative coordinates
                // This can be negative or beyond canvas bounds - that's okay!
                this.rawMousePos = {x: e.clientX - rect.left, y: e.clientY - rect.top};
            } else if (e.type === 'touchstart') {
                const touch = e.touches[0];
                this.mousePos = {x: touch.clientX, y: touch.clientY};
                // Convert screen position to canvas-relative coordinates
                // This can be negative or beyond canvas bounds - that's okay!
                this.rawMousePos = {x: touch.clientX - rect.left, y: touch.clientY - rect.top};
            }
            
            // Don't call updateBlockPreviews here as it will clear the preview
            // The preview will update when the block is placed or drag ends
        }
    }
    
    handleCanvasMouseMove(e) {
        if (this.isDragging) {
            e.preventDefault();
            const rect = this.canvas.getBoundingClientRect();
            // Get display-relative position (can be negative or beyond canvas display bounds)
            this.rawMousePos = {x: e.clientX - rect.left, y: e.clientY - rect.top};
            this.mousePos = {x: e.clientX, y: e.clientY};
            this.updateCursorFromMouse();
        }
    }
    
    handleCanvasTouchMove(e) {
        if (this.isDragging) {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = this.canvas.getBoundingClientRect();
            // Get display-relative position (can be negative or beyond canvas display bounds)
            this.rawMousePos = {x: touch.clientX - rect.left, y: touch.clientY - rect.top};
            this.mousePos = {x: touch.clientX, y: touch.clientY};
            this.updateCursorFromMouse();
        }
    }
    
    handleCanvasMouseUp(e) {
        if (this.isDragging && this.draggedBlock) {
            this.placeBlock();
            this.isDragging = false;
            this.draggedBlock = null;
        }
    }
    
    handleCanvasTouchEnd(e) {
        if (this.isDragging && this.draggedBlock) {
            e.preventDefault();
            this.placeBlock();
            this.isDragging = false;
            this.draggedBlock = null;
        }
    }
    
    updateCursorFromMouse() {
        const gridPos = this.screenToGrid(this.rawMousePos.x, this.rawMousePos.y);
        if (gridPos) {
            this.cursorPos = gridPos;
        }
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
        // Scale the display coordinates to canvas internal coordinates
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        const scaledX = x * scaleX;
        const scaledY = y * scaleY;
        
        const gridX = Math.floor((scaledX - this.GRID_OFFSET_X) / this.CELL_SIZE);
        const gridY = Math.floor((scaledY - this.GRID_OFFSET_Y) / this.CELL_SIZE);
        
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
            this.draggedBlock = this.selectedBlock;
            this.updateBlockPreviews();
        }
    }
    
    placeBlock() {
        if (!this.draggedBlock || this.draggedBlock.used) return;
        
        if (this.canPlaceBlock(this.draggedBlock, this.cursorPos)) {
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
        
        // Auto-select first block
        this.selectBlock(0);
        this.updateBlockPreviews();
    }
    
    updateBlockPreviews() {
        const previews = document.querySelectorAll('.block-preview');
        previews.forEach((preview, index) => {
            preview.classList.toggle('selected', index === this.selectedBlockIndex);
            
            if (this.availableBlocks[index]) {
                const block = this.availableBlocks[index];
                preview.style.opacity = block.used ? '0.3' : '1';
                
                // Clear previous content
                preview.innerHTML = '';
                
                // Create a container for the mini block
                const container = document.createElement('div');
                container.style.position = 'absolute';
                container.style.top = '50%';
                container.style.left = '50%';
                container.style.transform = 'translate(-50%, -50%)';
                container.style.pointerEvents = 'none';
                
                // Draw mini block shape
                const blockColor = this.COLORS.blocks[block.colorIndex % this.COLORS.blocks.length];
                const cellSize = 10;
                const gap = 2;
                
                // Calculate dimensions
                const blockWidth = block.shape[0].length;
                const blockHeight = block.shape.length;
                const totalWidth = blockWidth * (cellSize + gap) - gap;
                const totalHeight = blockHeight * (cellSize + gap) - gap;
                
                // Position relative to container center
                const startX = -totalWidth / 2;
                const startY = -totalHeight / 2;
                
                block.shape.forEach((row, y) => {
                    row.forEach((cell, x) => {
                        if (cell) {
                            const miniCell = document.createElement('div');
                            miniCell.style.position = 'absolute';
                            miniCell.style.width = cellSize + 'px';
                            miniCell.style.height = cellSize + 'px';
                            miniCell.style.backgroundColor = block.used ? '#666' : blockColor;
                            miniCell.style.left = (startX + x * (cellSize + gap)) + 'px';
                            miniCell.style.top = (startY + y * (cellSize + gap)) + 'px';
                            miniCell.style.borderRadius = '2px';
                            miniCell.style.boxShadow = '0 1px 2px rgba(0,0,0,0.3)';
                            container.appendChild(miniCell);
                        }
                    });
                });
                
                preview.appendChild(container);
                preview.style.backgroundColor = block.used ? 
                    'rgba(100,100,100,0.2)' : 
                    'rgba(255,255,255,0.1)';
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
        
        // Draw cursor only when not dragging
        if (!this.isDragging) {
            this.drawCursor();
        }
        
        // Draw block preview - either at cursor or following finger/mouse
        if (this.draggedBlock && !this.draggedBlock.used && this.isDragging) {
            this.drawDraggedBlock();
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
        const block = this.draggedBlock;
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
    
    drawDraggedBlock() {
        const block = this.draggedBlock;
        const color = this.COLORS.blocks[block.colorIndex % this.COLORS.blocks.length];
        
        // Get the display size vs internal canvas size
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        // Scale the raw mouse position to canvas coordinates
        const scaledX = this.rawMousePos.x * scaleX;
        const scaledY = this.rawMousePos.y * scaleY;
        
        const cellSize = this.CELL_SIZE;
        
        // Calculate block dimensions
        const blockWidth = block.shape[0].length * cellSize;
        const blockHeight = block.shape.length * cellSize;
        
        // Offset the block slightly to the left and up so it's visible while dragging
        // This prevents your finger from covering the block
        const fingerOffset = 60; // pixels to offset from finger position
        
        // Center the block on the cursor/finger position, then offset
        const offsetX = scaledX - blockWidth / 2 - fingerOffset;
        const offsetY = scaledY - blockHeight / 2 - fingerOffset;
        
        // Draw the block following the cursor
        this.ctx.fillStyle = color + 'CC'; // More opaque for visibility
        this.ctx.strokeStyle = '#fff';
        this.ctx.lineWidth = 2;
        
        block.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    const x = offsetX + dx * cellSize;
                    const y = offsetY + dy * cellSize;
                    
                    // Draw filled cell
                    this.ctx.fillRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                    
                    // Draw border
                    this.ctx.strokeRect(x + 2, y + 2, cellSize - 4, cellSize - 4);
                }
            });
        });
        
        // Also draw ghost preview on grid if valid position
        const gridPos = this.screenToGrid(this.rawMousePos.x, this.rawMousePos.y);
        if (gridPos && this.canPlaceBlock(block, gridPos)) {
            this.ctx.fillStyle = color + '40'; // Very transparent
            block.shape.forEach((row, dy) => {
                row.forEach((cell, dx) => {
                    if (cell) {
                        const gx = gridPos.x + dx;
                        const gy = gridPos.y + dy;
                        
                        if (gx >= 0 && gx < this.GRID_SIZE && gy >= 0 && gy < this.GRID_SIZE) {
                            this.ctx.fillRect(
                                this.GRID_OFFSET_X + gx * this.CELL_SIZE + 2,
                                this.GRID_OFFSET_Y + gy * this.CELL_SIZE + 2,
                                this.CELL_SIZE - 4,
                                this.CELL_SIZE - 4
                            );
                        }
                    }
                });
            });
        }
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
            
            // Line blocks (horizontal and vertical)
            [[1, 1]],
            [[1], [1]],
            [[1, 1, 1]],
            [[1], [1], [1]],
            [[1, 1, 1, 1]],
            [[1], [1], [1], [1]],
            
            // L shapes (all 4 rotations for each)
            [[1, 1], [1, 0]],
            [[1, 0], [1, 1]],
            [[0, 1], [1, 1]],
            [[1, 1], [0, 1]],
            
            // Bigger L shapes (all rotations)
            [[1, 1, 1], [1, 0, 0]],
            [[1, 1], [0, 1], [0, 1]],
            [[0, 0, 1], [1, 1, 1]],
            [[1, 0], [1, 0], [1, 1]],
            
            [[1, 1, 1], [0, 0, 1]],
            [[0, 1], [0, 1], [1, 1]],
            [[1, 0, 0], [1, 1, 1]],
            [[1, 1], [1, 0], [1, 0]],
            
            // Square
            [[1, 1], [1, 1]],
            
            // T shapes (all 4 rotations)
            [[1, 1, 1], [0, 1, 0]],
            [[0, 1], [1, 1], [0, 1]],
            [[0, 1, 0], [1, 1, 1]],
            [[1, 0], [1, 1], [1, 0]],
            
            // Z shapes (both orientations)
            [[1, 1, 0], [0, 1, 1]],
            [[0, 1], [1, 1], [1, 0]],
            [[0, 1, 1], [1, 1, 0]],
            [[1, 0], [1, 1], [0, 1]],
            
            // Plus shape
            [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            
            // Corner pieces (all rotations)
            [[1, 1], [1, 1], [1, 0]],
            [[1, 1], [1, 1], [0, 1]],
            [[1, 0], [1, 1], [1, 1]],
            [[0, 1], [1, 1], [1, 1]]
        ];
        
        this.shape = this.shapes[Math.floor(Math.random() * this.shapes.length)];
        this.colorIndex = Math.floor(Math.random() * 8) + 1;
        this.used = false;
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.game = new BlockWhackerGame('gameCanvas');
});