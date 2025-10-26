// Visual Effects Manager - Handles particles, animations, and text popups
import { COLORS } from '../utils/constants.js';

export class EffectsManager {
    constructor(game) {
        this.game = game;
        this.ctx = game.ctx;
        this.canvas = game.canvas;
        this.particles = [];
        this.textPopups = [];
    }
    
    update(deltaTime = 16) {
        // Update particles
        this.particles = this.particles.filter(particle => {
            particle.update(deltaTime);
            return particle.life > 0;
        });
        
        // Update text popups
        this.textPopups = this.textPopups.filter(popup => {
            popup.update(deltaTime);
            return popup.life > 0;
        });
    }
    
    draw() {
        // Draw particles
        this.particles.forEach(particle => particle.draw(this.ctx));
        
        // Draw text popups
        this.textPopups.forEach(popup => popup.draw(this.ctx));
    }
    
    // Create line clear effect
    createLineClearEffect(rows, cols) {
        const totalLines = rows.length + cols.length;
        const isCross = rows.length > 0 && cols.length > 0;
        
        // Determine message and particle count
        let message = '';
        let particleMultiplier = 1;
        
        if (isCross) {
            message = '🌟 CROSS! 🌟';
            particleMultiplier = 3;
        } else if (totalLines >= 4) {
            message = '🔥 AMAZING! 🔥';
            particleMultiplier = 2.5;
        } else if (totalLines === 3) {
            message = '⭐ AWESOME! ⭐';
            particleMultiplier = 2;
        } else if (totalLines === 2) {
            message = '✨ GREAT! ✨';
            particleMultiplier = 1.5;
        } else {
            message = '👍 NICE!';
        }
        
        // Create text popup at center
        this.createTextPopup(message, this.canvas.width / 2, this.canvas.height / 2, isCross);
        
        // Create particles for each cleared row
        rows.forEach(rowIndex => {
            const y = this.game.GRID_OFFSET_Y + rowIndex * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
            for (let i = 0; i < this.game.GRID_SIZE; i++) {
                const x = this.game.GRID_OFFSET_X + i * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                this.createParticleBurst(x, y, 8 * particleMultiplier, isCross);
            }
        });
        
        // Create particles for each cleared column
        cols.forEach(colIndex => {
            const x = this.game.GRID_OFFSET_X + colIndex * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
            for (let i = 0; i < this.game.GRID_SIZE; i++) {
                const y = this.game.GRID_OFFSET_Y + i * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                this.createParticleBurst(x, y, 8 * particleMultiplier, isCross);
            }
        });
    }
    
    createParticleBurst(x, y, count = 10, isCross = false) {
        for (let i = 0; i < count; i++) {
            const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
            const speed = 2 + Math.random() * 3;
            const color = isCross ? '#FFD700' : COLORS.blocks[Math.floor(Math.random() * COLORS.blocks.length)];
            
            this.particles.push(new Particle(x, y, angle, speed, color, isCross));
        }
    }
    
    createTextPopup(text, x, y, isSpecial = false) {
        this.textPopups.push(new TextPopup(text, x, y, isSpecial));
    }
    
    createBlockPlacementEffect(block, position) {
        // Small particle burst when placing a block
        block.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    const x = this.game.GRID_OFFSET_X + (position.x + dx) * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                    const y = this.game.GRID_OFFSET_Y + (position.y + dy) * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                    const color = COLORS.blocks[block.colorIndex % COLORS.blocks.length];
                    this.createParticleBurst(x, y, 3, false);
                }
            });
        });
    }
}

// Particle class
class Particle {
    constructor(x, y, angle, speed, color, isSpecial = false) {
        this.x = x;
        this.y = y;
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;
        this.color = color;
        this.life = 1.0;
        this.decay = 0.015 + Math.random() * 0.01;
        this.size = isSpecial ? 6 + Math.random() * 4 : 3 + Math.random() * 3;
        this.gravity = 0.1;
    }
    
    update(deltaTime) {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity; // Gravity effect
        this.life -= this.decay;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }
}

// Text popup class
class TextPopup {
    constructor(text, x, y, isSpecial = false) {
        this.text = text;
        this.x = x;
        this.y = y;
        this.life = 1.0;
        this.decay = 0.02;
        this.vy = -2; // Float upward
        this.fontSize = isSpecial ? 48 : 32;
        this.isSpecial = isSpecial;
    }
    
    update(deltaTime) {
        this.y += this.vy;
        this.life -= this.decay;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.font = `bold ${this.fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw shadow
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillText(this.text, this.x + 2, this.y + 2);
        
        // Draw text with gradient for special effects
        if (this.isSpecial) {
            const gradient = ctx.createLinearGradient(this.x - 100, this.y - 30, this.x + 100, this.y + 30);
            gradient.addColorStop(0, '#FFD700');
            gradient.addColorStop(0.5, '#FFA500');
            gradient.addColorStop(1, '#FFD700');
            ctx.fillStyle = gradient;
        } else {
            ctx.fillStyle = '#FFFFFF';
        }
        
        ctx.fillText(this.text, this.x, this.y);
        ctx.restore();
    }
}
