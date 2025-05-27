import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class TimeState:
    """État du temps pour un moment donné"""
    total_seconds: float
    total_frames: int
    physics_seconds: float
    physics_frames: int
    game_seconds: float
    game_frames: int

class TimeManager:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TimeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, fps: int = 60, post_physics_duration: float = 3.0):
        """
        Initialise le gestionnaire de temps.
        
        Args:
            fps (int): Images par seconde
            post_physics_duration (float): Durée en secondes après l'arrêt de la physique
        """
        if self._initialized:
            return
            
        self._initialized = True
        self.fps = fps
        self.post_physics_duration = post_physics_duration
        
        # Temps de démarrage
        self.start_time = time.time()
        self.frame_count = 0
        
        # Temps de la physique
        self.physics_start_time: Optional[float] = None
        self.physics_frame_count = 0
        self.physics_active = False
        
        # Temps du jeu (physique + post-physique)
        self.game_start_time: Optional[float] = None
        self.game_frame_count = 0
        self.game_active = False
        
        # Temps de fin de la physique
        self.physics_end_time: Optional[float] = None
    
    def start_physics(self) -> None:
        """Démarre le comptage du temps de la physique"""
        if not self.physics_active:
            self.physics_active = True
            self.physics_start_time = time.time()
            self.physics_frame_count = 0
            
            # Démarrer aussi le temps de jeu si ce n'est pas déjà fait
            if not self.game_active:
                self.game_active = True
                self.game_start_time = time.time()
                self.game_frame_count = 0
    
    def stop_physics(self) -> None:
        """Arrête le comptage du temps de la physique"""
        if self.physics_active:
            self.physics_active = False
            self.physics_end_time = time.time()
    
    def update_frame(self) -> None:
        """Met à jour les compteurs de frames"""
        self.frame_count += 1
        
        if self.physics_active:
            self.physics_frame_count += 1
        
        if self.game_active:
            self.game_frame_count += 1
            
            # Vérifier si on doit arrêter le temps de jeu
            if not self.physics_active and self.physics_end_time is not None:
                elapsed_since_physics = time.time() - self.physics_end_time
                if elapsed_since_physics >= self.post_physics_duration:
                    self.game_active = False
    
    def get_current_state(self) -> TimeState:
        """Retourne l'état actuel du temps"""
        # Calculer le temps total en fonction du nombre de frames
        total_seconds = self.frame_count / self.fps
        
        # Calculer le temps de la physique en fonction du nombre de frames
        physics_seconds = self.physics_frame_count / self.fps
        
        # Calculer le temps du jeu en fonction du nombre de frames
        game_seconds = self.game_frame_count / self.fps
        
        return TimeState(
            total_seconds=total_seconds,
            total_frames=self.frame_count,
            physics_seconds=physics_seconds,
            physics_frames=self.physics_frame_count,
            game_seconds=game_seconds,
            game_frames=self.game_frame_count
        )
    
    def format_time(self, seconds: float, include_frames: bool = True) -> str:
        """
        Formate un temps en secondes en une chaîne lisible.
        
        Args:
            seconds (float): Temps en secondes
            include_frames (bool): Inclure le nombre de frames
            
        Returns:
            str: Temps formaté
        """
        frames = int(seconds * self.fps)
        if include_frames:
            return f"{seconds:.2f}s ({frames}f)"
        return f"{seconds:.2f}s"
    
    def get_formatted_times(self) -> dict:
        """
        Retourne tous les temps formatés.
        
        Returns:
            dict: Dictionnaire des temps formatés
        """
        state = self.get_current_state()
        return {
            'total': self.format_time(state.total_seconds),
            'physics': self.format_time(state.physics_seconds),
            'game': self.format_time(state.game_seconds)
        }
    
    def reset(self) -> None:
        """Réinitialise tous les compteurs"""
        self.start_time = time.time()
        self.frame_count = 0
        self.physics_start_time = None
        self.physics_frame_count = 0
        self.physics_active = False
        self.game_start_time = None
        self.game_frame_count = 0
        self.game_active = False
        self.physics_end_time = None 