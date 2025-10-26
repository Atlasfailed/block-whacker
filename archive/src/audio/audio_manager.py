"""
Audio Manager - Handles all sound effects and music with standardized naming.
Provides comprehensive audio system for game events and background music.
"""

import pygame
import numpy as np
import math
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..config import AudioConfig, EffectsConfig


class SoundType(Enum):
    """Types of sound effects in the game."""
    BLOCK_PLACE = "block_place"
    LINE_CLEAR = "line_clear"
    COMBO = "combo"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    MENU_CLICK = "menu_click"
    ROTATION = "rotation"
    SELECTION = "selection"
    ERROR = "error"
    PAUSE = "pause"
    UNPAUSE = "unpause"
    HIGH_SCORE = "high_score"


class AudioChannel(Enum):
    """Audio channels for different types of sounds."""
    SOUND_EFFECTS = "sound_effects"
    MUSIC = "music"
    VOICE = "voice"
    AMBIENT = "ambient"


@dataclass
class SoundEffect:
    """Data structure for sound effects."""
    sound_type: SoundType
    sound_data: pygame.mixer.Sound
    volume_level: float = 1.0
    pitch_variation: float = 0.0
    channel_type: AudioChannel = AudioChannel.SOUND_EFFECTS
    is_looping: bool = False
    priority_level: int = 1  # Higher numbers = higher priority
    
    def play(self, volume_override: Optional[float] = None) -> Optional[pygame.mixer.Channel]:
        """Play the sound effect."""
        volume = volume_override if volume_override is not None else self.volume_level
        
        # Apply pitch variation if specified
        if self.pitch_variation > 0:
            pitch_factor = 1.0 + random.uniform(-self.pitch_variation, self.pitch_variation)
            # Note: pygame doesn't support pitch shifting directly, this is a placeholder
        
        self.sound_data.set_volume(volume)
        
        if self.is_looping:
            return self.sound_data.play(-1)  # Loop indefinitely
        else:
            return self.sound_data.play()


@dataclass
class MusicTrack:
    """Data structure for background music."""
    track_name: str
    file_path: Optional[str]
    volume_level: float = 0.7
    is_looping: bool = True
    fade_in_duration: float = 0.0
    fade_out_duration: float = 0.0
    generated_music: bool = False  # True if programmatically generated
    
    def load(self) -> bool:
        """Load the music track."""
        try:
            if self.file_path:
                pygame.mixer.music.load(self.file_path)
                return True
            return False
        except pygame.error:
            return False
    
    def play(self, start_position: float = 0.0) -> bool:
        """Play the music track."""
        try:
            loops = -1 if self.is_looping else 0
            
            if self.fade_in_duration > 0:
                pygame.mixer.music.play(loops, start_position, int(self.fade_in_duration * 1000))
            else:
                pygame.mixer.music.play(loops, start_position)
            
            pygame.mixer.music.set_volume(self.volume_level)
            return True
        except pygame.error:
            return False


class SoundGenerator:
    """Generates procedural sound effects."""
    
    @staticmethod
    def generate_tone(frequency: float, duration: float, sample_rate: int = 44100,
                     wave_type: str = 'sine') -> pygame.mixer.Sound:
        """Generate a tone with specified parameters."""
        frames = int(duration * sample_rate)
        
        # Generate waveform
        if wave_type == 'sine':
            wave_array = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
        elif wave_type == 'square':
            wave_array = np.sign(np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames)))
        elif wave_type == 'sawtooth':
            wave_array = 2 * (frequency * np.linspace(0, duration, frames) % 1) - 1
        elif wave_type == 'triangle':
            t = np.linspace(0, duration, frames)
            wave_array = 2 * np.abs(2 * (frequency * t % 1) - 1) - 1
        else:
            wave_array = np.sin(2 * np.pi * frequency * np.linspace(0, duration, frames))
        
        # Apply envelope (fade in/out to prevent clicks)
        envelope_length = min(frames // 20, int(0.01 * sample_rate))  # 1% of duration or 0.01s
        fade_in = np.linspace(0, 1, envelope_length)
        fade_out = np.linspace(1, 0, envelope_length)
        
        wave_array[:envelope_length] *= fade_in
        wave_array[-envelope_length:] *= fade_out
        
        # Convert to 16-bit integers
        wave_array = np.clip(wave_array * 32767, -32768, 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = wave_array  # Left channel
        stereo_array[:, 1] = wave_array  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)
    
    @staticmethod
    def generate_chord(frequencies: List[float], duration: float, 
                      sample_rate: int = 44100) -> pygame.mixer.Sound:
        """Generate a chord from multiple frequencies."""
        frames = int(duration * sample_rate)
        combined_wave = np.zeros(frames)
        
        for freq in frequencies:
            wave = np.sin(2 * np.pi * freq * np.linspace(0, duration, frames))
            combined_wave += wave / len(frequencies)  # Normalize amplitude
        
        # Apply envelope
        envelope_length = min(frames // 20, int(0.01 * sample_rate))
        fade_in = np.linspace(0, 1, envelope_length)
        fade_out = np.linspace(1, 0, envelope_length)
        
        combined_wave[:envelope_length] *= fade_in
        combined_wave[-envelope_length:] *= fade_out
        
        # Convert to 16-bit integers
        combined_wave = np.clip(combined_wave * 32767, -32768, 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = combined_wave
        stereo_array[:, 1] = combined_wave
        
        return pygame.sndarray.make_sound(stereo_array)
    
    @staticmethod
    def generate_noise(duration: float, noise_type: str = 'white',
                      sample_rate: int = 44100) -> pygame.mixer.Sound:
        """Generate noise sound effects."""
        frames = int(duration * sample_rate)
        
        if noise_type == 'white':
            noise_array = np.random.uniform(-1, 1, frames)
        elif noise_type == 'pink':
            # Simplified pink noise generation
            white_noise = np.random.uniform(-1, 1, frames)
            # Apply simple low-pass filter for pink-ish characteristics
            noise_array = np.convolve(white_noise, [0.1, 0.2, 0.4, 0.2, 0.1], mode='same')
        else:
            noise_array = np.random.uniform(-1, 1, frames)
        
        # Apply envelope
        envelope_length = min(frames // 10, int(0.05 * sample_rate))
        fade_in = np.linspace(0, 1, envelope_length)
        fade_out = np.linspace(1, 0, envelope_length)
        
        noise_array[:envelope_length] *= fade_in
        noise_array[-envelope_length:] *= fade_out
        
        # Convert to 16-bit integers
        noise_array = np.clip(noise_array * 32767, -32768, 32767).astype(np.int16)
        
        # Create stereo sound
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = noise_array
        stereo_array[:, 1] = noise_array
        
        return pygame.sndarray.make_sound(stereo_array)


class MusicGenerator:
    """Generates procedural background music."""
    
    # Musical scales and chord progressions
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # Semitones from root
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
    PENTATONIC_SCALE = [0, 2, 4, 7, 9]
    
    COMMON_PROGRESSIONS = [
        [0, 3, 5, 4],  # I-vi-V-IV
        [0, 5, 3, 4],  # I-V-vi-IV
        [3, 5, 0, 4],  # vi-V-I-IV
    ]
    
    @staticmethod
    def note_to_frequency(note: int, octave: int = 4) -> float:
        """Convert MIDI note number to frequency."""
        # A4 = 440 Hz = MIDI note 69
        return 440.0 * (2.0 ** ((note + octave * 12 - 69) / 12.0))
    
    @staticmethod
    def generate_simple_melody(duration: float, key: int = 60, 
                             scale: List[int] = None, 
                             tempo: float = 120.0) -> pygame.mixer.Sound:
        """Generate a simple melodic line."""
        if scale is None:
            scale = MusicGenerator.MAJOR_SCALE
        
        sample_rate = 44100
        frames = int(duration * sample_rate)
        
        # Calculate note duration based on tempo
        beat_duration = 60.0 / tempo  # Duration of one beat in seconds
        note_duration = beat_duration / 2  # Eighth notes
        
        melody_wave = np.zeros(frames)
        current_time = 0.0
        
        while current_time < duration:
            # Choose random note from scale
            scale_degree = random.choice(scale)
            note_freq = MusicGenerator.note_to_frequency(key + scale_degree)
            
            # Generate note
            note_frames = min(int(note_duration * sample_rate), frames - int(current_time * sample_rate))
            if note_frames <= 0:
                break
            
            start_frame = int(current_time * sample_rate)
            end_frame = start_frame + note_frames
            
            t = np.linspace(0, note_duration, note_frames)
            note_wave = np.sin(2 * np.pi * note_freq * t)
            
            # Apply envelope to note
            envelope_frames = min(note_frames // 4, int(0.05 * sample_rate))
            if envelope_frames > 0:
                fade_in = np.linspace(0, 1, envelope_frames)
                fade_out = np.linspace(1, 0, envelope_frames)
                note_wave[:envelope_frames] *= fade_in
                note_wave[-envelope_frames:] *= fade_out
            
            melody_wave[start_frame:end_frame] += note_wave * 0.3
            current_time += note_duration
        
        # Convert to audio format
        melody_wave = np.clip(melody_wave * 32767, -32768, 32767).astype(np.int16)
        
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = melody_wave
        stereo_array[:, 1] = melody_wave
        
        return pygame.sndarray.make_sound(stereo_array)


class AudioManager:
    """
    Main audio manager that handles all sound effects and music.
    Provides comprehensive audio system with standardized naming.
    """
    
    def __init__(self):
        """Initialize audio manager."""
        # Initialize pygame mixer
        pygame.mixer.pre_init(
            frequency=AudioConfig.SAMPLE_RATE,
            size=-16,  # 16-bit signed
            channels=AudioConfig.AUDIO_CHANNELS,
            buffer=AudioConfig.AUDIO_BUFFER_SIZE
        )
        pygame.mixer.init()
        
        # Sound storage
        self.sound_effects: Dict[SoundType, SoundEffect] = {}
        self.music_tracks: Dict[str, MusicTrack] = {}
        
        # Audio state
        self.master_volume = AudioConfig.MASTER_VOLUME
        self.sound_effects_volume = AudioConfig.SFX_VOLUME
        self.music_volume = AudioConfig.MUSIC_VOLUME
        
        self.sound_effects_enabled = True
        self.music_enabled = True
        
        # Current music state
        self.current_music_track: Optional[str] = None
        self.music_position = 0.0
        
        # Channel management
        self.audio_channels: Dict[AudioChannel, List[pygame.mixer.Channel]] = {}
        
        # Statistics
        self.sounds_played_total = 0
        self.sounds_per_type: Dict[SoundType, int] = {}
        
        # Initialize audio system
        self._initialize_sound_effects()
        self._initialize_music_tracks()
    
    def _initialize_sound_effects(self) -> None:
        """Initialize all sound effects."""
        try:
            # Generate procedural sound effects
            generator = SoundGenerator()
            
            # Block placement sound - soft click
            block_place_sound = generator.generate_tone(400, 0.1, wave_type='sine')
            self.sound_effects[SoundType.BLOCK_PLACE] = SoundEffect(
                sound_type=SoundType.BLOCK_PLACE,
                sound_data=block_place_sound,
                volume_level=0.6,
                pitch_variation=0.2
            )
            
            # Line clear sound - ascending tone
            line_clear_freqs = [523, 659, 784, 1047]  # C5, E5, G5, C6
            line_clear_sound = generator.generate_chord(line_clear_freqs, 0.5)
            self.sound_effects[SoundType.LINE_CLEAR] = SoundEffect(
                sound_type=SoundType.LINE_CLEAR,
                sound_data=line_clear_sound,
                volume_level=0.8,
                priority_level=3
            )
            
            # Combo sound - bell-like tones
            combo_freqs = [1047, 1319, 1568]  # C6, E6, G6
            combo_sound = generator.generate_chord(combo_freqs, 0.3)
            self.sound_effects[SoundType.COMBO] = SoundEffect(
                sound_type=SoundType.COMBO,
                sound_data=combo_sound,
                volume_level=0.7,
                priority_level=4
            )
            
            # Rotation sound - quick chirp
            rotation_sound = generator.generate_tone(800, 0.05, wave_type='triangle')
            self.sound_effects[SoundType.ROTATION] = SoundEffect(
                sound_type=SoundType.ROTATION,
                sound_data=rotation_sound,
                volume_level=0.4,
                pitch_variation=0.3
            )
            
            # Selection sound - soft beep
            selection_sound = generator.generate_tone(600, 0.08, wave_type='sine')
            self.sound_effects[SoundType.SELECTION] = SoundEffect(
                sound_type=SoundType.SELECTION,
                sound_data=selection_sound,
                volume_level=0.5
            )
            
            # Error sound - dissonant tone
            error_sound = generator.generate_tone(200, 0.2, wave_type='square')
            self.sound_effects[SoundType.ERROR] = SoundEffect(
                sound_type=SoundType.ERROR,
                sound_data=error_sound,
                volume_level=0.6,
                priority_level=2
            )
            
            # Game over sound - descending tones
            game_over_freqs = [523, 466, 415, 349]  # C5, Bb4, Ab4, F4
            game_over_sound = generator.generate_chord(game_over_freqs, 1.0)
            self.sound_effects[SoundType.GAME_OVER] = SoundEffect(
                sound_type=SoundType.GAME_OVER,
                sound_data=game_over_sound,
                volume_level=0.8,
                priority_level=5
            )
            
            # Level up sound - triumphant chord
            level_up_freqs = [523, 659, 784, 1047, 1319]  # C major pentatonic
            level_up_sound = generator.generate_chord(level_up_freqs, 0.8)
            self.sound_effects[SoundType.LEVEL_UP] = SoundEffect(
                sound_type=SoundType.LEVEL_UP,
                sound_data=level_up_sound,
                volume_level=0.9,
                priority_level=5
            )
            
            # Menu click - simple click
            menu_click_sound = generator.generate_tone(1000, 0.03, wave_type='sine')
            self.sound_effects[SoundType.MENU_CLICK] = SoundEffect(
                sound_type=SoundType.MENU_CLICK,
                sound_data=menu_click_sound,
                volume_level=0.4
            )
            
            # Pause/unpause sounds
            pause_sound = generator.generate_tone(440, 0.15, wave_type='triangle')
            self.sound_effects[SoundType.PAUSE] = SoundEffect(
                sound_type=SoundType.PAUSE,
                sound_data=pause_sound,
                volume_level=0.5
            )
            
            unpause_sound = generator.generate_tone(660, 0.15, wave_type='triangle')
            self.sound_effects[SoundType.UNPAUSE] = SoundEffect(
                sound_type=SoundType.UNPAUSE,
                sound_data=unpause_sound,
                volume_level=0.5
            )
            
            # High score sound - fanfare
            high_score_freqs = [1047, 1319, 1568, 2093]  # C6, E6, G6, C7
            high_score_sound = generator.generate_chord(high_score_freqs, 1.2)
            self.sound_effects[SoundType.HIGH_SCORE] = SoundEffect(
                sound_type=SoundType.HIGH_SCORE,
                sound_data=high_score_sound,
                volume_level=0.9,
                priority_level=5
            )
            
        except Exception as e:
            print(f"Warning: Could not initialize some sound effects: {e}")
    
    def _initialize_music_tracks(self) -> None:
        """Initialize background music tracks."""
        try:
            # Generate procedural background music
            music_generator = MusicGenerator()
            
            # Main game music - ambient melody
            main_game_music = music_generator.generate_simple_melody(
                duration=60.0,  # 1 minute loop
                key=60,  # C4
                scale=MusicGenerator.PENTATONIC_SCALE,
                tempo=100.0
            )
            
            # Save as temporary file for pygame.mixer.music
            # Note: In a full implementation, you'd save this to a file
            # For now, we'll create a placeholder track
            self.music_tracks['main_game'] = MusicTrack(
                track_name='main_game',
                file_path=None,  # Would be path to saved file
                volume_level=0.3,
                is_looping=True,
                generated_music=True
            )
            
            self.music_tracks['menu'] = MusicTrack(
                track_name='menu',
                file_path=None,
                volume_level=0.4,
                is_looping=True,
                generated_music=True
            )
            
        except Exception as e:
            print(f"Warning: Could not initialize music tracks: {e}")
    
    def play_sound_effect(self, sound_type: SoundType, 
                         volume_override: Optional[float] = None) -> bool:
        """Play a sound effect."""
        if not self.sound_effects_enabled or sound_type not in self.sound_effects:
            return False
        
        sound_effect = self.sound_effects[sound_type]
        
        # Calculate final volume
        final_volume = (volume_override if volume_override is not None 
                       else sound_effect.volume_level)
        final_volume *= self.sound_effects_volume * self.master_volume
        
        # Play sound
        channel = sound_effect.play(final_volume)
        
        if channel:
            # Update statistics
            self.sounds_played_total += 1
            self.sounds_per_type[sound_type] = self.sounds_per_type.get(sound_type, 0) + 1
            return True
        
        return False
    
    def play_music(self, track_name: str, fade_in_duration: float = 0.0) -> bool:
        """Play background music."""
        if not self.music_enabled or track_name not in self.music_tracks:
            return False
        
        track = self.music_tracks[track_name]
        
        # Stop current music
        self.stop_music()
        
        # Load and play new track
        if track.generated_music:
            # For generated music, we'd need to implement a different approach
            # For now, just track the current music
            self.current_music_track = track_name
            return True
        else:
            success = track.load()
            if success:
                track.fade_in_duration = fade_in_duration
                success = track.play()
                if success:
                    self.current_music_track = track_name
                    pygame.mixer.music.set_volume(track.volume_level * self.music_volume * self.master_volume)
            
            return success
    
    def stop_music(self, fade_out_duration: float = 0.0) -> None:
        """Stop background music."""
        if pygame.mixer.music.get_busy():
            if fade_out_duration > 0:
                pygame.mixer.music.fadeout(int(fade_out_duration * 1000))
            else:
                pygame.mixer.music.stop()
        
        self.current_music_track = None
    
    def pause_music(self) -> None:
        """Pause background music."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Resume background music."""
        pygame.mixer.music.unpause()
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_sound_effects_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sound_effects_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def _update_music_volume(self) -> None:
        """Update the current music volume."""
        if self.current_music_track and pygame.mixer.music.get_busy():
            track = self.music_tracks.get(self.current_music_track)
            if track:
                final_volume = track.volume_level * self.music_volume * self.master_volume
                pygame.mixer.music.set_volume(final_volume)
    
    def set_sound_effects_enabled(self, enabled: bool) -> None:
        """Enable or disable sound effects."""
        self.sound_effects_enabled = enabled
        if not enabled:
            # Stop all currently playing sound effects
            pygame.mixer.stop()
    
    def set_music_enabled(self, enabled: bool) -> None:
        """Enable or disable music."""
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
    
    def toggle_sound_effects(self) -> bool:
        """Toggle sound effects on/off. Returns new state."""
        self.set_sound_effects_enabled(not self.sound_effects_enabled)
        return self.sound_effects_enabled
    
    def toggle_music(self) -> bool:
        """Toggle music on/off. Returns new state."""
        self.set_music_enabled(not self.music_enabled)
        return self.music_enabled
    
    def get_current_music_track(self) -> Optional[str]:
        """Get the currently playing music track name."""
        return self.current_music_track
    
    def is_music_playing(self) -> bool:
        """Check if music is currently playing."""
        return pygame.mixer.music.get_busy()
    
    def get_audio_statistics(self) -> Dict[str, Any]:
        """Get audio system statistics."""
        return {
            'sounds_played_total': self.sounds_played_total,
            'sounds_per_type': dict(self.sounds_per_type),
            'current_music_track': self.current_music_track,
            'music_playing': self.is_music_playing(),
            'sound_effects_enabled': self.sound_effects_enabled,
            'music_enabled': self.music_enabled,
            'master_volume': self.master_volume,
            'sound_effects_volume': self.sound_effects_volume,
            'music_volume': self.music_volume,
            'available_sound_effects': list(self.sound_effects.keys()),
            'available_music_tracks': list(self.music_tracks.keys())
        }
    
    def reset_statistics(self) -> None:
        """Reset audio statistics."""
        self.sounds_played_total = 0
        self.sounds_per_type.clear()
    
    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop_music()
        pygame.mixer.stop()
        pygame.mixer.quit()
    
    def __repr__(self) -> str:
        """String representation of audio manager."""
        return (f"AudioManager(sounds_enabled={self.sound_effects_enabled}, "
                f"music_enabled={self.music_enabled}, "
                f"current_track={self.current_music_track})")