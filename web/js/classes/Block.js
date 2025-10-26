// Block Class - Represents a tetris-like block piece
export class Block {
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
