/**
 * SVG graphics for game effects
 * Creates custom drawn graphics instead of using emojis
 */

export const SVGEffects = {
    /**
     * Create a star particle SVG
     */
    createStar(size, color) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        const centerX = size / 2;
        const centerY = size / 2;
        const outerRadius = size / 2;
        const innerRadius = size / 4;
        const points = 5;
        
        ctx.beginPath();
        for (let i = 0; i < points * 2; i++) {
            const radius = i % 2 === 0 ? outerRadius : innerRadius;
            const angle = (i * Math.PI) / points - Math.PI / 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.closePath();
        
        // Gradient fill
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, outerRadius);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, this.adjustBrightness(color, -30));
        
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Outer glow
        ctx.strokeStyle = this.adjustBrightness(color, 50);
        ctx.lineWidth = 2;
        ctx.stroke();
        
        return canvas;
    },
    
    /**
     * Create a sparkle/diamond particle
     */
    createSparkle(size, color) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        const centerX = size / 2;
        const centerY = size / 2;
        
        ctx.beginPath();
        ctx.moveTo(centerX, 0);
        ctx.lineTo(centerX + size * 0.15, centerY);
        ctx.lineTo(centerX, size);
        ctx.lineTo(centerX - size * 0.15, centerY);
        ctx.closePath();
        
        // Horizontal beam
        ctx.moveTo(0, centerY);
        ctx.lineTo(centerX, centerY - size * 0.15);
        ctx.lineTo(size, centerY);
        ctx.lineTo(centerX, centerY + size * 0.15);
        ctx.closePath();
        
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, size / 2);
        gradient.addColorStop(0, '#ffffff');
        gradient.addColorStop(0.5, color);
        gradient.addColorStop(1, this.adjustBrightness(color, -40));
        
        ctx.fillStyle = gradient;
        ctx.fill();
        
        return canvas;
    },
    
    /**
     * Create a circle particle
     */
    createCircle(size, color) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = size / 2;
        
        const gradient = ctx.createRadialGradient(
            centerX - radius * 0.3, 
            centerY - radius * 0.3, 
            0, 
            centerX, 
            centerY, 
            radius
        );
        gradient.addColorStop(0, '#ffffff');
        gradient.addColorStop(0.4, color);
        gradient.addColorStop(1, this.adjustBrightness(color, -50));
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        
        return canvas;
    },
    
    /**
     * Create a flame particle
     */
    createFlame(size, isOrange = true) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        const centerX = size / 2;
        const baseY = size * 0.9;
        
        // Flame shape
        ctx.beginPath();
        ctx.moveTo(centerX, size * 0.1);
        ctx.bezierCurveTo(
            size * 0.8, size * 0.3,
            size * 0.9, size * 0.6,
            centerX, baseY
        );
        ctx.bezierCurveTo(
            size * 0.1, size * 0.6,
            size * 0.2, size * 0.3,
            centerX, size * 0.1
        );
        ctx.closePath();
        
        const gradient = ctx.createLinearGradient(centerX, size * 0.1, centerX, baseY);
        if (isOrange) {
            gradient.addColorStop(0, '#fff9e6');
            gradient.addColorStop(0.3, '#ffeb3b');
            gradient.addColorStop(0.6, '#ff9800');
            gradient.addColorStop(1, '#ff5722');
        } else {
            gradient.addColorStop(0, '#e6f7ff');
            gradient.addColorStop(0.3, '#4dd0ff');
            gradient.addColorStop(0.6, '#0099ff');
            gradient.addColorStop(1, '#0066cc');
        }
        
        ctx.fillStyle = gradient;
        ctx.fill();
        
        return canvas;
    },
    
    /**
     * Create a thumbs up icon
     */
    createThumbsUp(size) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        ctx.fillStyle = '#ffd700';
        ctx.strokeStyle = '#ff8800';
        ctx.lineWidth = size * 0.05;
        ctx.lineJoin = 'round';
        
        // Thumb
        ctx.beginPath();
        ctx.moveTo(size * 0.4, size * 0.3);
        ctx.lineTo(size * 0.6, size * 0.1);
        ctx.lineTo(size * 0.7, size * 0.15);
        ctx.lineTo(size * 0.55, size * 0.35);
        
        // Fingers
        ctx.lineTo(size * 0.8, size * 0.35);
        ctx.lineTo(size * 0.8, size * 0.55);
        ctx.lineTo(size * 0.75, size * 0.6);
        ctx.lineTo(size * 0.75, size * 0.7);
        ctx.lineTo(size * 0.7, size * 0.75);
        ctx.lineTo(size * 0.7, size * 0.85);
        ctx.lineTo(size * 0.3, size * 0.85);
        ctx.lineTo(size * 0.3, size * 0.4);
        ctx.closePath();
        
        ctx.fill();
        ctx.stroke();
        
        return canvas;
    },
    
    /**
     * Create a trophy/award icon
     */
    createTrophy(size, color) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        const gradient = ctx.createLinearGradient(0, 0, 0, size);
        gradient.addColorStop(0, this.adjustBrightness(color, 40));
        gradient.addColorStop(1, this.adjustBrightness(color, -20));
        
        ctx.fillStyle = gradient;
        ctx.strokeStyle = this.adjustBrightness(color, -40);
        ctx.lineWidth = size * 0.04;
        
        // Cup body
        ctx.beginPath();
        ctx.moveTo(size * 0.3, size * 0.2);
        ctx.lineTo(size * 0.25, size * 0.5);
        ctx.quadraticCurveTo(size * 0.3, size * 0.6, size * 0.5, size * 0.6);
        ctx.quadraticCurveTo(size * 0.7, size * 0.6, size * 0.75, size * 0.5);
        ctx.lineTo(size * 0.7, size * 0.2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Handles
        ctx.beginPath();
        ctx.arc(size * 0.2, size * 0.35, size * 0.1, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(size * 0.8, size * 0.35, size * 0.1, 0, Math.PI * 2);
        ctx.stroke();
        
        // Base
        ctx.fillRect(size * 0.35, size * 0.6, size * 0.3, size * 0.05);
        ctx.fillRect(size * 0.25, size * 0.75, size * 0.5, size * 0.1);
        
        return canvas;
    },
    
    /**
     * Create a skull icon for game over
     */
    createSkull(size) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');
        
        ctx.fillStyle = '#cccccc';
        ctx.strokeStyle = '#666666';
        ctx.lineWidth = size * 0.05;
        
        // Skull
        ctx.beginPath();
        ctx.arc(size * 0.5, size * 0.4, size * 0.3, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        
        // Eye sockets
        ctx.fillStyle = '#000000';
        ctx.beginPath();
        ctx.arc(size * 0.35, size * 0.35, size * 0.08, 0, Math.PI * 2);
        ctx.arc(size * 0.65, size * 0.35, size * 0.08, 0, Math.PI * 2);
        ctx.fill();
        
        // Nose
        ctx.beginPath();
        ctx.moveTo(size * 0.5, size * 0.45);
        ctx.lineTo(size * 0.45, size * 0.52);
        ctx.lineTo(size * 0.55, size * 0.52);
        ctx.closePath();
        ctx.fill();
        
        // Jaw
        ctx.fillStyle = '#cccccc';
        ctx.strokeStyle = '#666666';
        ctx.fillRect(size * 0.3, size * 0.6, size * 0.4, size * 0.25);
        ctx.strokeRect(size * 0.3, size * 0.6, size * 0.4, size * 0.25);
        
        // Teeth
        ctx.fillStyle = '#000000';
        for (let i = 0; i < 5; i++) {
            ctx.fillRect(size * (0.32 + i * 0.08), size * 0.6, size * 0.04, size * 0.1);
        }
        
        return canvas;
    },
    
    /**
     * Adjust color brightness
     */
    adjustBrightness(color, amount) {
        // Convert hex to RGB
        let r, g, b;
        if (color.startsWith('#')) {
            const hex = color.slice(1);
            r = parseInt(hex.substr(0, 2), 16);
            g = parseInt(hex.substr(2, 2), 16);
            b = parseInt(hex.substr(4, 2), 16);
        } else if (color.startsWith('rgb')) {
            [r, g, b] = color.match(/\d+/g).map(Number);
        } else {
            return color;
        }
        
        // Adjust
        r = Math.max(0, Math.min(255, r + amount));
        g = Math.max(0, Math.min(255, g + amount));
        b = Math.max(0, Math.min(255, b + amount));
        
        return `rgb(${r}, ${g}, ${b})`;
    },
    
    /**
     * Get random particle type for effects
     */
    getRandomParticle(size, color, type = 'mixed') {
        switch(type) {
            case 'stars':
                return this.createStar(size, color);
            case 'sparkles':
                return this.createSparkle(size, color);
            case 'flames':
                return this.createFlame(size, true);
            case 'circles':
                return this.createCircle(size, color);
            case 'mixed':
            default:
                const types = [
                    () => this.createStar(size, color),
                    () => this.createSparkle(size, color),
                    () => this.createCircle(size, color)
                ];
                return types[Math.floor(Math.random() * types.length)]();
        }
    }
};
