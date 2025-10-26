// Visual Effects Manager - Handles particles, animations, and text popups
import { COLORS } from '../utils/constants.js';
import { SVGEffects } from '../utils/svgEffects.js';

export class EffectsManager {
    constructor(game) {
        this.game = game;
        this.ctx = game.ctx;
        this.canvas = game.canvas;
        this.particles = [];
        this.textPopups = [];
        this.iconPopups = [];
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
        
        // Update icon popups
        this.iconPopups = this.iconPopups.filter(popup => {
            popup.update(deltaTime);
            return popup.life > 0;
        });
    }
    
    draw() {
        // Draw particles
        this.particles.forEach(particle => particle.draw(this.ctx));
        
        // Draw icon popups
        this.iconPopups.forEach(popup => popup.draw(this.ctx));
        
        // Draw text popups
        this.textPopups.forEach(popup => popup.draw(this.ctx));
    }
    
    // Create line clear effect
    createLineClearEffect(rows, cols) {
        const totalLines = rows.length + cols.length;
        const isCross = rows.length > 0 && cols.length > 0;
        
        // Determine message, icon type, and particle count
        let message = '';
        let iconType = null;
        let particleMultiplier = 1;
        let particleType = 'mixed';
        
        if (isCross) {
            message = 'CROSS!';
            iconType = 'trophy';
            particleMultiplier = 3;
            particleType = 'stars';
        } else if (totalLines >= 4) {
            message = 'AMAZING!';
            iconType = 'trophy';
            particleMultiplier = 2.5;
            particleType = 'flames';
        } else if (totalLines === 3) {
            message = 'AWESOME!';
            iconType = 'star';
            particleMultiplier = 2;
            particleType = 'stars';
        } else if (totalLines === 2) {
            message = 'GREAT!';
            iconType = 'sparkle';
            particleMultiplier = 1.5;
            particleType = 'sparkles';
        } else {
            message = 'NICE!';
            iconType = 'thumbsup';
        }
        
        // Create icon and text popup at center
        this.createIconTextPopup(iconType, message, this.canvas.width / 2, this.canvas.height / 2, isCross);
        
        // Create particles for each cleared row
        rows.forEach(rowIndex => {
            const y = this.game.GRID_OFFSET_Y + rowIndex * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
            for (let i = 0; i < this.game.GRID_SIZE; i++) {
                const x = this.game.GRID_OFFSET_X + i * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                this.createParticleBurst(x, y, 8 * particleMultiplier, isCross, particleType);
            }
        });
        
        // Create particles for each cleared column
        cols.forEach(colIndex => {
            const x = this.game.GRID_OFFSET_X + colIndex * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
            for (let i = 0; i < this.game.GRID_SIZE; i++) {
                const y = this.game.GRID_OFFSET_Y + i * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                this.createParticleBurst(x, y, 8 * particleMultiplier, isCross, particleType);
            }
        });
    }
    
    createParticleBurst(x, y, count = 10, isCross = false, particleType = 'mixed') {
        for (let i = 0; i < count; i++) {
            const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
            const speed = 2 + Math.random() * 3;
            const color = isCross ? '#FFD700' : COLORS.blocks[Math.floor(Math.random() * COLORS.blocks.length)];
            
            this.particles.push(new Particle(x, y, angle, speed, color, isCross, particleType));
        }
    }
    
    createTextPopup(text, x, y, isSpecial = false) {
        this.textPopups.push(new TextPopup(text, x, y, isSpecial));
    }
    
    createIconTextPopup(iconType, text, x, y, isSpecial = false) {
        this.iconPopups.push(new IconTextPopup(iconType, text, x, y, isSpecial));
    }
    
    createBlockPlacementEffect(block, position) {
        // Small particle burst when placing a block
        block.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    const x = this.game.GRID_OFFSET_X + (position.x + dx) * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                    const y = this.game.GRID_OFFSET_Y + (position.y + dy) * this.game.CELL_SIZE + this.game.CELL_SIZE / 2;
                    const color = COLORS.blocks[block.colorIndex % COLORS.blocks.length];
                    this.createParticleBurst(x, y, 3, false, 'circles');
                }
            });
        });
    }
}

// Particle class
class Particle {
    constructor(x, y, angle, speed, color, isSpecial = false, particleType = 'mixed') {
        this.x = x;
        this.y = y;
        this.vx = Math.cos(angle) * speed;
        this.vy = Math.sin(angle) * speed;
        this.color = color;
        this.life = 1.0;
        this.decay = 0.015 + Math.random() * 0.01;
        this.size = isSpecial ? 8 + Math.random() * 6 : 4 + Math.random() * 4;
        this.gravity = 0.1;
        this.rotation = Math.random() * Math.PI * 2;
        this.rotationSpeed = (Math.random() - 0.5) * 0.3;
        
        // Create SVG graphic for this particle
        this.graphic = SVGEffects.getRandomParticle(this.size * 2, color, particleType);
    }
    
    update(deltaTime) {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity; // Gravity effect
        this.rotation += this.rotationSpeed;
        this.life -= this.decay;
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.translate(this.x, this.y);
        ctx.rotate(this.rotation);
        ctx.drawImage(this.graphic, -this.size, -this.size, this.size * 2, this.size * 2);
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

// Icon and Text popup class
class IconTextPopup {
    constructor(iconType, text, x, y, isSpecial = false) {
        this.iconType = iconType;
        this.text = text;
        this.x = x;
        this.y = y;
        this.life = 1.0;
        this.decay = 0.015;
        this.vy = -1.5; // Float upward
        this.fontSize = isSpecial ? 36 : 28;
        this.iconSize = isSpecial ? 60 : 48;
        this.isSpecial = isSpecial;
        this.scale = 0;
        this.targetScale = 1;
        
        // Create the icon graphic
        const color = isSpecial ? '#FFD700' : '#4FC3F7';
        switch(iconType) {
            case 'trophy':
                this.icon = SVGEffects.createTrophy(this.iconSize, color);
                break;
            case 'star':
                this.icon = SVGEffects.createStar(this.iconSize, color);
                break;
            case 'sparkle':
                this.icon = SVGEffects.createSparkle(this.iconSize, color);
                break;
            case 'thumbsup':
                this.icon = SVGEffects.createThumbsUp(this.iconSize);
                break;
            case 'skull':
                this.icon = SVGEffects.createSkull(this.iconSize);
                break;
            default:
                this.icon = SVGEffects.createStar(this.iconSize, color);
        }
    }
    
    update(deltaTime) {
        this.y += this.vy;
        this.life -= this.decay;
        
        // Pop-in animation
        if (this.scale < this.targetScale) {
            this.scale += 0.1;
            if (this.scale > this.targetScale) this.scale = this.targetScale;
        }
    }
    
    draw(ctx) {
        ctx.save();
        ctx.globalAlpha = this.life;
        
        // Draw icon
        ctx.translate(this.x, this.y - 30);
        ctx.scale(this.scale, this.scale);
        ctx.drawImage(this.icon, -this.iconSize / 2, -this.iconSize / 2);
        ctx.restore();
        
        // Draw text
        ctx.save();
        ctx.globalAlpha = this.life;
        ctx.font = `bold ${this.fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        
        // Draw shadow
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillText(this.text, this.x + 2, this.y + 32);
        
        // Draw text with gradient for special effects
        if (this.isSpecial) {
            const gradient = ctx.createLinearGradient(this.x - 80, this.y, this.x + 80, this.y + 40);
            gradient.addColorStop(0, '#FFD700');
            gradient.addColorStop(0.5, '#FFA500');
            gradient.addColorStop(1, '#FFD700');
            ctx.fillStyle = gradient;
        } else {
            ctx.fillStyle = '#FFFFFF';
        }
        
        ctx.fillText(this.text, this.x, this.y + 30);
        ctx.restore();
    }
}
