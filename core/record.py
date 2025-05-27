import os
import pygame
import imageio
import imageio_ffmpeg
import numpy as np
import pandas as pd
import soundfile as sf
import subprocess
from typing import Optional, Tuple
from core.audio import AudioManager
from core.time import TimeManager
import time
from config import VISUAL, FPS, TEMPS_LIMITE, DELAI_ARRET, OUTPUT_DIR
from scipy import signal  # Ajout de l'import pour le rééchantillonnage

class RecordManager:
    def __init__(self, width: int, height: int, fps: int = FPS):
        """
        Initialise le gestionnaire d'enregistrement.
        
        Args:
            width (int): Largeur de la vidéo
            height (int): Hauteur de la vidéo
            fps (int): Images par seconde
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.max_frames = FPS * TEMPS_LIMITE + FPS * DELAI_ARRET
        self.writer = None
        self.recording = False
        self.frame_count = 0
        self.recording_started = False
        self.output_dir = OUTPUT_DIR
        self.video_path = None
        
        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def start_recording(self, video_name: str = 'simulation.mp4') -> None:
        """
        Démarre l'enregistrement vidéo.
        
        Args:
            video_name (str): Nom du fichier vidéo de sortie
        """
        if not self.recording:
            self.video_path = os.path.join(self.output_dir, video_name)
            self.writer = imageio.get_writer(
                self.video_path,
                fps=self.fps,
                quality=8,
                macro_block_size=16,
                ffmpeg_params=[
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart',
                    '-profile:v', 'high',
                    '-level', '4.2',
                    '-r', str(self.fps),
                    '-threads', '0',
                    '-tune', 'zerolatency'
                ]
            )
            self.recording = True
            self.frame_count = 0
            self.recording_started = False
    
    def record_frame(self, screen: pygame.Surface) -> bool:
        """
        Enregistre une frame de la simulation.
        
        Args:
            screen (pygame.Surface): Surface Pygame à enregistrer
            
        Returns:
            bool: True si l'enregistrement continue, False si terminé
        """
        if not self.recording or self.writer is None or self.frame_count >= self.max_frames:
            return False
            
        try:
            if not self.recording_started:
                self.recording_started = True
                print(f"Début de l'enregistrement")
                print(f"Dimensions de la vidéo: {self.width}x{self.height}")
                print(f"FPS: {self.fps}")
            
            # Convertir la surface en tableau numpy
            frame = pygame.surfarray.array3d(screen)
            frame = frame.transpose([1, 0, 2])
            
            # Vérifier que la frame n'est pas vide
            if frame.size == 0:
                print(f"Erreur: Frame vide détectée à {self.frame_count}")
                return True
            
            # Vérifier les dimensions de la frame
            if frame.shape[0] != self.height or frame.shape[1] != self.width:
                print(f"Erreur: Dimensions incorrectes de la frame: {frame.shape} au lieu de ({self.height}, {self.width}, 3)")
                return True
            
            # Enregistrer la frame
            try:
                self.writer.append_data(frame)
                self.frame_count += 1
                
                # Mettre à jour le temps de la simulation en fonction du nombre de frames
                simulation_time = self.frame_count / self.fps
                if self.frame_count % 100 == 0:
                    print(f"Frame {self.frame_count} enregistrée (temps: {simulation_time:.2f}s)")
            except Exception as e:
                print(f"Erreur lors de l'enregistrement de la frame {self.frame_count}: {e}")
                import gc
                gc.collect()
                return True
            
            if self.frame_count >= self.max_frames:
                print(f"Enregistrement terminé: {self.frame_count} frames enregistrées")
                return False
                
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'enregistrement de la frame : {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_recording(self) -> None:
        """Arrête l'enregistrement et ferme le writer."""
        if self.writer is not None:
            self.writer.close()
            self.writer = None
        self.recording = False
        print(f"Enregistrement vidéo terminé. {self.frame_count} frames enregistrées.")
    
    def is_recording(self) -> bool:
        """Retourne True si l'enregistrement est en cours."""
        return self.recording
    
    def get_frame_count(self) -> int:
        """Retourne le nombre de frames enregistrées."""
        return self.frame_count
    
    def get_recording_progress(self) -> float:
        """Retourne la progression de l'enregistrement (0.0 à 1.0)."""
        return self.frame_count / self.max_frames if self.max_frames > 0 else 0.0
    
    def get_video_path(self) -> Optional[str]:
        """Retourne le chemin de la vidéo enregistrée."""
        return self.video_path 