"""
Effects Manager - Handles visual effects, animations, and particle systems.
Provides comprehensive visual feedback for game events with standardized naming.
"""

import pygame
import math
import random
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

from ..config import (
    DisplayConfig,
    ColorPalette,
    EffectsConfig,
    FontConfig,
)
from ..core.block_manager import BlockPosition


class EffectType(Enum):
    """Types of visual effects."""
    LINE_CLEAR = "line_clear"
    BLOCK_PLACEMENT = "block_placement"
    SCORE_POPUP = "score_popup"
    COMBO_FLASH = "combo_flash"
    GAME_OVER_TRANSITION = "game_over_transition"
    LEVEL_UP = "level_up"
    EXPLOSION = "explosion"
    SPARKLE = "sparkle"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SHAKE = "shake"
    GLOW = "glow"


@dataclass
class ParticleData:
    """Data structure for individual particles."""
    position_x: float
    position_y: float
    velocity_x: float
    velocity_y: float
    color_rgb: Tuple[int, int, int]
    size: float
    life_time: float
    max_life_time: float
    fade_alpha: int = 255
    gravity: float = 0.0
    friction: float = 0.99
    
    def update(self, delta_time: float) -> bool:
        """Update particle state. Returns True if particle is still alive."""
        self.position_x += self.velocity_x * delta_time
        self.position_y += self.velocity_y * delta_time
        
        self.velocity_x *= self.friction
        self.velocity_y += self.gravity * delta_time
        self.velocity_y *= self.friction
        
        self.life_time -= delta_time
        
        # Update alpha based on remaining life
        life_ratio = max(0, self.life_time / self.max_life_time)
        self.fade_alpha = int(255 * life_ratio)
        
        return self.life_time > 0
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the particle."""
        if self.fade_alpha <= 0:
            return
        
        particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        # Ensure valid RGBA color format
        r, g, b = self.color_rgb[:3]  # Take only first 3 components
        alpha = max(0, min(255, int(self.fade_alpha)))  # Clamp alpha to 0-255
        color_rgba = (r, g, b, alpha)
        pygame.draw.circle(particle_surface, color_rgba,
                          (self.size, self.size), self.size)
        
        surface.blit(particle_surface, (self.position_x - self.size, self.position_y - self.size))


@dataclass
class EffectInstance:
    """Instance of a visual effect."""
    effect_type: EffectType
    position_x: float
    position_y: float
    duration: float
    elapsed_time: float = 0.0
    is_active: bool = True
    properties: Dict[str, Any] = field(default_factory=dict)
    particles: List[ParticleData] = field(default_factory=list)
    
    def update(self, delta_time: float) -> bool:
        """Update effect state. Returns True if effect is still active."""
        if not self.is_active:
            return False
        
        self.elapsed_time += delta_time
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(delta_time)]
        
        # Check if effect should end
        if self.elapsed_time >= self.duration:
            self.is_active = False
            return False
        
        return True
    
    def get_progress_ratio(self) -> float:
        """Get effect progress as ratio (0.0 to 1.0)."""
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed_time / self.duration)
    
    def get_fade_alpha(self) -> int:
        """Get current alpha value for fading effects."""
        progress = self.get_progress_ratio()
        
        if self.effect_type in [EffectType.FADE_OUT, EffectType.GAME_OVER_TRANSITION]:
            return int(255 * (1.0 - progress))
        elif self.effect_type == EffectType.FADE_IN:
            return int(255 * progress)
        else:
            return 255


class LineCloseEffect:
    """Specialized effect for line clearing animations."""
    
    @staticmethod
    def create_line_clear_effect(row_positions: List[int], grid_offset_x: int, 
                               grid_offset_y: int, cell_size: int) -> EffectInstance:
        """Create a line clear effect for specified rows."""
        effect = EffectInstance(
            effect_type=EffectType.LINE_CLEAR,
            position_x=grid_offset_x,
            position_y=grid_offset_y + (min(row_positions) * cell_size),
            duration=EffectsConfig.LINE_CLEAR_DURATION,
            properties={
                'rows': row_positions,
                'grid_offset_x': grid_offset_x,
                'grid_offset_y': grid_offset_y,
                'cell_size': cell_size,
                'flash_count': 0,
                'flash_interval': 0.1
            }
        )
        
        # Create explosion particles for each cleared cell
        for row_idx in row_positions:
            for col_idx in range(DisplayConfig.GRID_SIZE):
                center_x = grid_offset_x + col_idx * cell_size + cell_size // 2
                center_y = grid_offset_y + row_idx * cell_size + cell_size // 2
                
                # Create multiple particles per cell
                for _ in range(EffectsConfig.PARTICLES_PER_CELL):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(50, 150)
                    
                    particle = ParticleData(
                        position_x=center_x,
                        position_y=center_y,
                        velocity_x=math.cos(angle) * speed,
                        velocity_y=math.sin(angle) * speed,
                        color_rgb=random.choice([ColorPalette.SCORE_COLOR, ColorPalette.WARNING_COLOR,
                                               ColorPalette.HIGHLIGHT_COLOR]),
                        size=random.uniform(2, 5),
                        life_time=random.uniform(0.5, 1.5),
                        max_life_time=random.uniform(0.5, 1.5),
                        gravity=100,
                        friction=0.95
                    )
                    effect.particles.append(particle)
        
        return effect
    
    @staticmethod
    def render_line_clear_effect(effect: EffectInstance, surface: pygame.Surface) -> None:
        """Render line clear effect."""
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Flash effect
        flash_interval = props.get('flash_interval', 0.1)
        flash_phase = (effect.elapsed_time % flash_interval) / flash_interval
        
        if flash_phase < 0.5:  # Flash on
            for row_idx in props['rows']:
                for col_idx in range(DisplayConfig.GRID_SIZE):
                    cell_rect = pygame.Rect(
                        props['grid_offset_x'] + col_idx * props['cell_size'],
                        props['grid_offset_y'] + row_idx * props['cell_size'],
                        props['cell_size'],
                        props['cell_size']
                    )
                    
                    # Create pulsing white overlay
                    flash_surface = pygame.Surface((props['cell_size'], props['cell_size']))
                    flash_alpha = int(200 * (1.0 - progress))
                    flash_surface.set_alpha(flash_alpha)
                    flash_surface.fill(ColorPalette.WHITE)
                    
                    surface.blit(flash_surface, cell_rect)
        
        # Render particles
        for particle in effect.particles:
            particle.render(surface)


class ScorePopupEffect:
    """Effect for displaying score popups."""
    
    @staticmethod
    def create_score_popup(score_value: int, position: Tuple[float, float]) -> EffectInstance:
        """Create a score popup effect."""
        x, y = position
        
        effect = EffectInstance(
            effect_type=EffectType.SCORE_POPUP,
            position_x=x,
            position_y=y,
            duration=EffectsConfig.COMBO_DISPLAY_DURATION,
            properties={
                'score_value': score_value,
                'start_y': y,
                'rise_distance': 80,
                'font_size': FontConfig.FONT_SIZE_MEDIUM
            }
        )
        
        return effect
    
    @staticmethod
    def render_score_popup(effect: EffectInstance, surface: pygame.Surface) -> None:
        """Render score popup effect."""
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Calculate position with rising motion
        current_y = props['start_y'] - (progress * props['rise_distance'])
        
        # Create score text
        font = pygame.font.Font(None, props['font_size'])
        score_text = f"+{props['score_value']:,}"
        
        # Color based on score value
        if props['score_value'] >= 1000:
            color = ColorPalette.WARNING_COLOR
        elif props['score_value'] >= 500:
            color = ColorPalette.SCORE_COLOR
        else:
            color = ColorPalette.TEXT_PRIMARY
        
        text_surface = font.render(score_text, FontConfig.TEXT_ANTIALIAS, color)
        
        # Apply fade out
        alpha = effect.get_fade_alpha()
        if alpha < 255:
            text_surface.set_alpha(alpha)
        
        # Center text
        text_rect = text_surface.get_rect(center=(effect.position_x, current_y))
        
        # Shadow for better visibility
        shadow_surface = font.render(score_text, FontConfig.TEXT_ANTIALIAS, ColorPalette.BLACK)
        shadow_surface.set_alpha(alpha // 2)
        shadow_rect = shadow_surface.get_rect(center=(effect.position_x + 2, current_y + 2))
        
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)


class ComboEffect:
    """Effect for combo indicators and celebrations."""
    
    @staticmethod
    def create_combo_flash(combo_count: int) -> EffectInstance:
        """Create a combo flash effect."""
        effect = EffectInstance(
            effect_type=EffectType.COMBO_FLASH,
            position_x=DisplayConfig.WINDOW_WIDTH // 2,
            position_y=100,
            duration=EffectsConfig.COMBO_FLASH_DURATION,
            properties={
                'combo_count': combo_count,
                'pulse_frequency': 3.0,  # Pulses per second
                'max_scale': 1.5
            }
        )
        
        # Create celebratory particles
        for _ in range(combo_count * 5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 200)
            
            particle = ParticleData(
                position_x=effect.position_x,
                position_y=effect.position_y,
                velocity_x=math.cos(angle) * speed,
                velocity_y=math.sin(angle) * speed,
                color_rgb=random.choice([ColorPalette.WARNING_COLOR, ColorPalette.HIGHLIGHT_COLOR,
                                       ColorPalette.SCORE_COLOR]),
                size=random.uniform(3, 8),
                life_time=random.uniform(1.0, 2.0),
                max_life_time=random.uniform(1.0, 2.0),
                gravity=50,
                friction=0.98
            )
            effect.particles.append(particle)
        
        return effect
    
    @staticmethod
    def render_combo_flash(effect: EffectInstance, surface: pygame.Surface) -> None:
        """Render combo flash effect."""
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Pulsing scale
        pulse_phase = math.sin(effect.elapsed_time * props['pulse_frequency'] * 2 * math.pi)
        scale = 1.0 + (pulse_phase * 0.5 * props['max_scale'] * (1.0 - progress))
        
        # Create combo text
        font_size = int(FontConfig.FONT_SIZE_LARGE * scale)
        font = pygame.font.Font(None, font_size)
        combo_text = f"COMBO x{props['combo_count']}!"
        
        text_surface = font.render(combo_text, FontConfig.TEXT_ANTIALIAS, ColorPalette.WARNING_COLOR)
        
        # Apply fade and glow effect
        alpha = effect.get_fade_alpha()
        if alpha < 255:
            text_surface.set_alpha(alpha)
        
        text_rect = text_surface.get_rect(center=(effect.position_x, effect.position_y))
        
        # Glow effect
        glow_surface = font.render(combo_text, FontConfig.TEXT_ANTIALIAS, ColorPalette.WHITE)
        glow_surface.set_alpha(alpha // 3)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_rect = glow_surface.get_rect(center=(effect.position_x + offset[0], 
                                                     effect.position_y + offset[1]))
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(text_surface, text_rect)
        
        # Render particles
        for particle in effect.particles:
            particle.render(surface)


class ScreenShakeEffect:
    """Screen shake effect for impactful events."""
    
    @staticmethod
    def create_screen_shake(intensity: float, duration: float) -> EffectInstance:
        """Create a screen shake effect."""
        return EffectInstance(
            effect_type=EffectType.SHAKE,
            position_x=0,
            position_y=0,
            duration=duration,
            properties={
                'intensity': intensity,
                'frequency': 20.0  # Shakes per second
            }
        )
    
    @staticmethod
    def get_shake_offset(effect: EffectInstance) -> Tuple[int, int]:
        """Get current shake offset."""
        if not effect.is_active:
            return (0, 0)
        
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Decrease intensity over time
        current_intensity = props['intensity'] * (1.0 - progress)
        
        # Calculate shake
        shake_x = math.sin(effect.elapsed_time * props['frequency'] * 2 * math.pi) * current_intensity
        shake_y = math.cos(effect.elapsed_time * props['frequency'] * 1.7 * math.pi) * current_intensity
        
        return (int(shake_x), int(shake_y))


class BlockPlacementEffect:
    """Effect for successful block placements."""
    
    @staticmethod
    def create_placement_effect(positions: List[BlockPosition], 
                              grid_offset_x: int, grid_offset_y: int, 
                              cell_size: int, block_color: Tuple[int, int, int]) -> EffectInstance:
        """Create block placement effect."""
        # Calculate center position
        if positions:
            center_x = grid_offset_x + (sum(p.x for p in positions) / len(positions)) * cell_size + cell_size // 2
            center_y = grid_offset_y + (sum(p.y for p in positions) / len(positions)) * cell_size + cell_size // 2
        else:
            center_x = grid_offset_x + cell_size // 2
            center_y = grid_offset_y + cell_size // 2
        
        effect = EffectInstance(
            effect_type=EffectType.BLOCK_PLACEMENT,
            position_x=center_x,
            position_y=center_y,
            duration=EffectsConfig.BLOCK_PLACEMENT_ANIMATION_DURATION,
            properties={
                'positions': positions,
                'grid_offset_x': grid_offset_x,
                'grid_offset_y': grid_offset_y,
                'cell_size': cell_size,
                'block_color': block_color
            }
        )
        
        # Create placement particles
        for position in positions:
            cell_center_x = grid_offset_x + position.x * cell_size + cell_size // 2
            cell_center_y = grid_offset_y + position.y * cell_size + cell_size // 2
            
            for _ in range(3):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(20, 60)
                
                particle = ParticleData(
                    position_x=cell_center_x,
                    position_y=cell_center_y,
                    velocity_x=math.cos(angle) * speed,
                    velocity_y=math.sin(angle) * speed,
                    color_rgb=block_color,
                    size=random.uniform(1, 3),
                    life_time=random.uniform(0.3, 0.8),
                    max_life_time=random.uniform(0.3, 0.8),
                    gravity=20,
                    friction=0.96
                )
                effect.particles.append(particle)
        
        return effect
    
    @staticmethod
    def render_placement_effect(effect: EffectInstance, surface: pygame.Surface) -> None:
        """Render block placement effect."""
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Brief highlight of placed cells
        if progress < 0.5:
            highlight_alpha = int(100 * (1.0 - progress * 2))
            
            for position in props['positions']:
                cell_rect = pygame.Rect(
                    props['grid_offset_x'] + position.x * props['cell_size'],
                    props['grid_offset_y'] + position.y * props['cell_size'],
                    props['cell_size'],
                    props['cell_size']
                )
                
                highlight_surface = pygame.Surface((props['cell_size'], props['cell_size']))
                highlight_surface.set_alpha(highlight_alpha)
                highlight_surface.fill(ColorPalette.WHITE)
                
                surface.blit(highlight_surface, cell_rect)
        
        # Render particles
        for particle in effect.particles:
            particle.render(surface)


class EffectsManager:
    """
    Main effects manager that handles all visual effects and animations.
    Provides comprehensive effect system with standardized naming.
    """
    
    def __init__(self):
        """Initialize effects manager."""
        self.active_effects: List[EffectInstance] = []
        self.screen_shake_offset = (0, 0)
        self.global_effects_enabled = True
        
        # Effect statistics
        self.total_effects_created = 0
        self.effects_per_type: Dict[EffectType, int] = {}
    
    def create_line_clear_effect(self, cleared_rows: List[int]) -> None:
        """Create line clear effect for specified rows."""
        if not self.global_effects_enabled or not cleared_rows:
            return
        
        effect = LineCloseEffect.create_line_clear_effect(
            cleared_rows,
            DisplayConfig.GRID_OFFSET_X,
            DisplayConfig.GRID_OFFSET_Y,
            DisplayConfig.CELL_SIZE
        )
        
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.LINE_CLEAR)
    
    def create_score_popup(self, score_value: int, position: Tuple[float, float]) -> None:
        """Create score popup effect."""
        if not self.global_effects_enabled:
            return
        
        effect = ScorePopupEffect.create_score_popup(score_value, position)
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.SCORE_POPUP)
    
    def create_combo_flash(self, combo_count: int) -> None:
        """Create combo flash effect."""
        if not self.global_effects_enabled or combo_count <= 1:
            return
        
        effect = ComboEffect.create_combo_flash(combo_count)
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.COMBO_FLASH)
    
    def create_screen_shake(self, intensity: float, duration: float = 0.3) -> None:
        """Create screen shake effect."""
        if not self.global_effects_enabled:
            return
        
        effect = ScreenShakeEffect.create_screen_shake(intensity, duration)
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.SHAKE)
    
    def create_block_placement_effect(self, positions: List[BlockPosition], 
                                    block_color: Tuple[int, int, int]) -> None:
        """Create block placement effect."""
        if not self.global_effects_enabled:
            return
        
        effect = BlockPlacementEffect.create_placement_effect(
            positions,
            DisplayConfig.GRID_OFFSET_X,
            DisplayConfig.GRID_OFFSET_Y,
            DisplayConfig.CELL_SIZE,
            block_color
        )
        
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.BLOCK_PLACEMENT)
    
    def create_level_up_effect(self, level: int) -> None:
        """Create level up celebration effect."""
        if not self.global_effects_enabled:
            return
        
        # Create multiple effects for level up
        self.create_screen_shake(8.0, 0.5)
        
        # Create sparkle effect
        effect = EffectInstance(
            effect_type=EffectType.LEVEL_UP,
            position_x=DisplayConfig.WINDOW_WIDTH // 2,
            position_y=DisplayConfig.WINDOW_HEIGHT // 2,
            duration=2.0,
            properties={
                'level': level,
                'sparkle_count': 50
            }
        )
        
        # Create sparkle particles
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 200)
            speed = random.uniform(30, 80)
            
            particle = ParticleData(
                position_x=effect.position_x + math.cos(angle) * distance,
                position_y=effect.position_y + math.sin(angle) * distance,
                velocity_x=math.cos(angle) * speed,
                velocity_y=math.sin(angle) * speed,
                color_rgb=random.choice([ColorPalette.WARNING_COLOR, ColorPalette.SCORE_COLOR,
                                       ColorPalette.HIGHLIGHT_COLOR, ColorPalette.WHITE]),
                size=random.uniform(2, 6),
                life_time=random.uniform(1.5, 3.0),
                max_life_time=random.uniform(1.5, 3.0),
                gravity=20,
                friction=0.98
            )
            effect.particles.append(particle)
        
        self.active_effects.append(effect)
        self._register_effect_creation(EffectType.LEVEL_UP)
    
    def update_effects(self, delta_time: float) -> None:
        """Update all active effects."""
        # Update effects and remove finished ones
        self.active_effects = [effect for effect in self.active_effects 
                              if effect.update(delta_time)]
        
        # Update screen shake offset
        shake_effects = [e for e in self.active_effects if e.effect_type == EffectType.SHAKE]
        if shake_effects:
            # Combine shake effects
            total_x, total_y = 0, 0
            for effect in shake_effects:
                offset_x, offset_y = ScreenShakeEffect.get_shake_offset(effect)
                total_x += offset_x
                total_y += offset_y
            
            self.screen_shake_offset = (total_x, total_y)
        else:
            self.screen_shake_offset = (0, 0)
    
    def render_effects(self, surface: pygame.Surface) -> None:
        """Render all active effects."""
        if not self.global_effects_enabled:
            return
        
        for effect in self.active_effects:
            if not effect.is_active:
                continue
            
            if effect.effect_type == EffectType.LINE_CLEAR:
                LineCloseEffect.render_line_clear_effect(effect, surface)
            elif effect.effect_type == EffectType.SCORE_POPUP:
                ScorePopupEffect.render_score_popup(effect, surface)
            elif effect.effect_type == EffectType.COMBO_FLASH:
                ComboEffect.render_combo_flash(effect, surface)
            elif effect.effect_type == EffectType.BLOCK_PLACEMENT:
                BlockPlacementEffect.render_placement_effect(effect, surface)
            elif effect.effect_type == EffectType.LEVEL_UP:
                self._render_level_up_effect(effect, surface)
            else:
                # Render generic particle effects
                for particle in effect.particles:
                    particle.render(surface)
    
    def _render_level_up_effect(self, effect: EffectInstance, surface: pygame.Surface) -> None:
        """Render level up effect."""
        props = effect.properties
        progress = effect.get_progress_ratio()
        
        # Level up text with pulsing effect
        pulse = math.sin(effect.elapsed_time * 4 * math.pi) * 0.2 + 1.0
        font_size = int(FontConfig.FONT_SIZE_LARGE * pulse)
        font = pygame.font.Font(None, font_size)
        
        level_text = f"LEVEL {props['level']}!"
        text_surface = font.render(level_text, FontConfig.TEXT_ANTIALIAS, ColorPalette.WARNING_COLOR)
        
        alpha = int(255 * (1.0 - progress))
        text_surface.set_alpha(alpha)
        
        text_rect = text_surface.get_rect(center=(effect.position_x, effect.position_y - 50))
        surface.blit(text_surface, text_rect)
        
        # Render sparkle particles
        for particle in effect.particles:
            particle.render(surface)
    
    def clear_effects(self) -> None:
        """Clear all active effects."""
        self.active_effects.clear()
        self.screen_shake_offset = (0, 0)
    
    def set_effects_enabled(self, enabled: bool) -> None:
        """Enable or disable all effects."""
        self.global_effects_enabled = enabled
        if not enabled:
            self.clear_effects()
    
    def get_screen_shake_offset(self) -> Tuple[int, int]:
        """Get current screen shake offset."""
        return self.screen_shake_offset
    
    def get_active_effects_count(self) -> int:
        """Get number of active effects."""
        return len(self.active_effects)
    
    def get_effects_statistics(self) -> Dict[str, Any]:
        """Get effects usage statistics."""
        return {
            'total_effects_created': self.total_effects_created,
            'active_effects_count': len(self.active_effects),
            'effects_per_type': dict(self.effects_per_type),
            'effects_enabled': self.global_effects_enabled
        }
    
    def _register_effect_creation(self, effect_type: EffectType) -> None:
        """Register creation of an effect for statistics."""
        self.total_effects_created += 1
        self.effects_per_type[effect_type] = self.effects_per_type.get(effect_type, 0) + 1
    
    def __repr__(self) -> str:
        """String representation of effects manager."""
        return (f"EffectsManager(active={len(self.active_effects)}, "
                f"enabled={self.global_effects_enabled}, "
                f"total_created={self.total_effects_created})")