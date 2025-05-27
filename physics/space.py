import pymunk
from typing import Tuple

class PhysicsSpace:
    """Gestionnaire de l'espace physique."""
    
    def __init__(self, gravity: Tuple[float, float] = (0, 900)):
        """
        Initialise l'espace physique.
        
        Args:
            gravity (Tuple[float, float]): Vecteur de gravité (x, y)
        """
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self._configure_space()
    
    def _configure_space(self):
        """Configure les paramètres de l'espace physique."""
        self.space.collision_bias = 0.2
        self.space.iterations = 20
    
    def step(self, dt: float):
        """
        Fait avancer la simulation physique.
        
        Args:
            dt (float): Pas de temps
        """
        self.space.step(dt)
    
    def get_space(self) -> pymunk.Space:
        """
        Retourne l'espace physique.
        
        Returns:
            pymunk.Space: L'espace physique
        """
        return self.space
    
    def reset(self):
        """Réinitialise l'espace physique."""
        for body in self.space.bodies:
            self.space.remove(body)
        for shape in self.space.shapes:
            self.space.remove(shape)
        self._configure_space() 