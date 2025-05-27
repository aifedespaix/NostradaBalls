import pygame
import os
import subprocess
import random
from dataclasses import dataclass
from typing import Dict, List, Optional
from core.time import TimeManager
from config import VISUAL, REPONSE_A_VOICE_PATH, REPONSE_B_VOICE_PATH, QUESTION_SOUND_PATH, BACKGROUND_MUSIC_PATH, BACKGROUND_MUSIC_VOLUME

@dataclass
class SoundEvent:
    """Classe pour stocker les informations d'un événement sonore"""
    sound_name: str
    frame_number: int
    time_seconds: float

class AudioManager:
    _instance = None
    
    # Sons sans variation de pitch
    SOUND_PATHS = {
        'reponse_a': REPONSE_A_VOICE_PATH,
        'reponse_b': REPONSE_B_VOICE_PATH,
        'question': QUESTION_SOUND_PATH,
        'background': BACKGROUND_MUSIC_PATH
    }
    
    # Sons avec variation de pitch
    SOUND_VARIATION_PATHS = {
        'default': "assets/sounds/default_collision.wav",
        'A': "assets/sounds/A.wav",
        'B': "assets/sounds/B.wav"
    }
    
    # Volumes par défaut
    SOUND_VOLUMES = {
        'default': 0.05,
        'A': 0.05,
        'B': 0.08,
        'reponse_a': 1,
        'reponse_b': 1,
        'question': 1,
        'background': BACKGROUND_MUSIC_VOLUME
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AudioManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.sound_events: List[SoundEvent] = []
        self.current_frame = 0
        self.is_recording = False
        self.time_manager = TimeManager()
        
        # Initialisation du mixer pygame
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.2)  # Volume global réduit à 20%
        
        # Chargement automatique des sons
        self.load_all_sounds()
        
        # Génération des variations de pitch
        self.generate_pitch_variations()
    
    def load_all_sounds(self) -> None:
        """Charge tous les sons définis dans SOUND_PATHS et SOUND_VARIATION_PATHS"""
        # Chargement des sons sans variation
        for name, path in self.SOUND_PATHS.items():
            self.load_sound(name, path, self.SOUND_VOLUMES.get(name, 1.0))
            
        # Chargement des sons avec variation
        for name, path in self.SOUND_VARIATION_PATHS.items():
            self.load_sound(name, path, self.SOUND_VOLUMES.get(name, 1.0))
    
    def load_sound(self, name: str, path: str, volume: float = 1.0) -> None:
        """Charge un son et le stocke dans le dictionnaire"""
        if name not in self.sounds:
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Erreur lors du chargement du son {name}: {e}")
    
    def get_sound_path(self, name: str) -> Optional[str]:
        """Retourne le chemin du son demandé"""
        return self.SOUND_PATHS.get(name)
    
    def get_sound_volume(self, name: str) -> float:
        """Retourne le volume du son demandé"""
        return self.SOUND_VOLUMES.get(name, 1.0)
    
    def play_sound(self, name: str) -> None:
        """Joue un son et enregistre l'événement si l'enregistrement est actif"""
        if name in self.sounds:
            if VISUAL:
                self.sounds[name].play()
            
            if self.is_recording:
                current_time = self.time_manager.get_current_state().physics_seconds
                event = SoundEvent(
                    sound_name=name,
                    frame_number=self.current_frame,
                    time_seconds=current_time
                )
                self.sound_events.append(event)
    
    def start_recording(self) -> None:
        """Démarre l'enregistrement des événements sonores"""
        self.is_recording = True
        self.sound_events.clear()
    
    def stop_recording(self) -> None:
        """Arrête l'enregistrement des événements sonores"""
        self.is_recording = False
    
    def update_frame(self, frame_number: int) -> None:
        """Met à jour le numéro de frame actuel"""
        self.current_frame = frame_number
    
    def get_sound_events(self) -> List[SoundEvent]:
        """Retourne la liste des événements sonores enregistrés"""
        return self.sound_events
    
    def export_sound_events(self, filepath: str) -> None:
        """Exporte les événements sonores dans un fichier texte"""
        try:
            with open(filepath, 'w') as f:
                f.write("Frame,Time(s),Sound\n")
                for event in self.sound_events:
                    f.write(f"{int(event.frame_number)},{event.time_seconds:.3f},{event.sound_name}\n")
        except Exception as e:
            print(f"Erreur lors de l'export des événements sonores: {e}")
    
    def reset(self) -> None:
        """Réinitialise le gestionnaire audio"""
        self.sound_events.clear()
        self.current_frame = 0
        self.is_recording = False
    
    def generate_pitch_variations(self) -> None:
        """Génère les variations de pitch pour tous les sons définis dans SOUND_VARIATION_PATHS"""
        pitch_variations = {
            '1': 1.03,  # +3%
            '2': 1.06,  # +6%
            '3': 1.09,  # +9%
            '4': 0.97,  # -3%
            '5': 0.94,  # -6%
            '6': 0.91   # -9%
        }
        
        for sound_name, sound_path in self.SOUND_VARIATION_PATHS.items():
            if not os.path.exists(sound_path):
                print(f"Le fichier {sound_path} n'existe pas")
                continue
                
            base_name = os.path.splitext(sound_path)[0]
            
            for variation, pitch_factor in pitch_variations.items():
                output_path = f"{base_name}-{variation}.wav"
                
                if not os.path.exists(output_path):
                    try:
                        cmd = [
                            'ffmpeg',
                            '-i', sound_path,
                            '-af', f'asetrate=44100*{pitch_factor},aresample=44100',
                            '-y',  # Écraser le fichier s'il existe
                            output_path
                        ]
                        
                        subprocess.run(cmd, check=True, capture_output=True)
                        print(f"Variation {variation} générée pour {sound_name}")
                        
                    except subprocess.CalledProcessError as e:
                        print(f"Erreur lors de la génération de la variation {variation} pour {sound_name}: {e}")
                    except Exception as e:
                        print(f"Erreur inattendue pour {sound_name}: {e}")
    
    def get_random_sound_variation(self, sound_name: str) -> str:
        """Retourne un chemin de son aléatoire parmi les variations disponibles"""
        # Vérifier si le son est dans les sons avec variation
        if sound_name not in self.SOUND_VARIATION_PATHS:
            return self.SOUND_PATHS.get(sound_name)
            
        base_path = self.SOUND_VARIATION_PATHS[sound_name]
        base_name = os.path.splitext(base_path)[0]
        variations = [base_path]  # Version originale
        
        # Ajouter les variations 1-6 si elles existent
        for i in range(1, 7):
            variation_path = f"{base_name}-{i}.wav"
            if os.path.exists(variation_path):
                variations.append(variation_path)
                
        return random.choice(variations) 