// Game Configuration Constants
export const GAME_CONFIG = {
    GRID_SIZE: 8,
    CELL_SIZE: 40,
    GRID_OFFSET_X: 50,
    GRID_OFFSET_Y: 50
};

export const COLORS = {
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

export const SCORING = {
    BASE_SCORE: 100,
    MULTIPLIERS: {
        1: 1,
        2: 3,
        3: 6,
        4: 10,
        default: 15
    }
};
