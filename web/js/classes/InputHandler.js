// Input Handler - Manages all mouse, touch, and keyboard input
import { screenToGrid } from '../utils/coordinates.js';

export class InputHandler {
    constructor(game) {
        this.game = game;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const game = this.game;
        const canvas = game.canvas;
        
        // Canvas mouse/touch events for dragging
        canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        canvas.addEventListener('touchmove', (e) => this.handleCanvasTouchMove(e), {passive: false});
        canvas.addEventListener('touchend', (e) => this.handleCanvasTouchEnd(e), {passive: false});
        
        // Global mouse/touch events for dragging outside canvas
        document.addEventListener('mousemove', (e) => {
            if (game.isDragging) {
                this.handleCanvasMouseMove(e);
            }
        });
        document.addEventListener('mouseup', (e) => {
            if (game.isDragging) {
                this.handleCanvasMouseUp(e);
            }
        });
        document.addEventListener('touchmove', (e) => {
            if (game.isDragging) {
                this.handleCanvasTouchMove(e);
            }
        }, {passive: false});
        document.addEventListener('touchend', (e) => {
            if (game.isDragging) {
                this.handleCanvasTouchEnd(e);
            }
        }, {passive: false});
        
        // Block preview dragging
        document.querySelectorAll('.block-preview').forEach((preview, index) => {
            preview.addEventListener('mousedown', (e) => this.startDragFromPreview(e, index));
            preview.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.startDragFromPreview(e, index);
            }, {passive: false});
        });
        
        // Control buttons
        document.getElementById('undoBtn').addEventListener('click', () => game.undo());
        document.getElementById('resetBtn').addEventListener('click', () => game.resetGame());
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
    }
    
    handleKeyDown(e) {
        const game = this.game;
        
        switch(e.key) {
            case 'ArrowUp':
                e.preventDefault();
                game.moveCursor(0, -1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                game.moveCursor(0, 1);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                game.moveCursor(-1, 0);
                break;
            case 'ArrowRight':
                e.preventDefault();
                game.moveCursor(1, 0);
                break;
            case ' ':
            case 'Enter':
                e.preventDefault();
                if (game.selectedBlock && !game.selectedBlock.used) {
                    game.tryPlaceBlock();
                }
                break;
            case 'Escape':
                e.preventDefault();
                game.selectedBlock = null;
                game.selectedBlockIndex = -1;
                game.updateBlockPreviews();
                break;
        }
    }
    
    startDragFromPreview(e, index) {
        const game = this.game;
        const block = game.availableBlocks[index];
        
        if (!block || block.used) return;
        
        game.selectedBlock = block;
        game.selectedBlockIndex = index;
        game.draggedBlock = block;
        game.isDragging = true;
        
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        const rect = game.canvas.getBoundingClientRect();
        
        game.rawMousePos = {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
        
        game.updateCursorFromMouse();
        game.updateBlockPreviews();
    }
    
    handleCanvasMouseMove(e) {
        const game = this.game;
        const rect = game.canvas.getBoundingClientRect();
        
        game.rawMousePos = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        if (game.isDragging) {
            game.updateCursorFromMouse();
        }
    }
    
    handleCanvasMouseUp(e) {
        const game = this.game;
        
        if (game.isDragging && game.draggedBlock) {
            if (game.canPlaceBlock(game.draggedBlock, game.cursorPos)) {
                game.tryPlaceBlock();
            }
            game.isDragging = false;
            game.draggedBlock = null;
        }
    }
    
    handleCanvasTouchMove(e) {
        e.preventDefault();
        const game = this.game;
        const rect = game.canvas.getBoundingClientRect();
        const touch = e.touches[0];
        
        game.rawMousePos = {
            x: touch.clientX - rect.left,
            y: touch.clientY - rect.top
        };
        
        if (game.isDragging) {
            game.updateCursorFromMouse();
        }
    }
    
    handleCanvasTouchEnd(e) {
        e.preventDefault();
        const game = this.game;
        
        if (game.isDragging && game.draggedBlock) {
            if (game.canPlaceBlock(game.draggedBlock, game.cursorPos)) {
                game.tryPlaceBlock();
            }
            game.isDragging = false;
            game.draggedBlock = null;
        }
    }
}
