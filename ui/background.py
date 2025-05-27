import pygame
import os
from typing import Optional, List
from utils.color import create_gradient_surface
from utils.image import create_cover_image
from config import *

class Background:
    """Gestionnaire du fond du jeu."""
    
    def __init__(self, width: int, height: int):
        """
        Initialise le fond du jeu.
        
        Args:
            width (int): Largeur de l'écran
            height (int): Hauteur de l'écran
        """
        self.width = width
        self.height = height
        self.background = None
        self.gradient_surfaces = self._create_gradient_surfaces()
        self._load_background()
    
    def _create_gradient_surfaces(self) -> List[pygame.Surface]:
        """
        Crée les surfaces de dégradé pour les fonds.
        
        Returns:
            List[pygame.Surface]: Liste des surfaces de dégradé
        """
        gradient_surfaces = []
        for i in range(2):
            start_color = CUVE_B_COLOR_START if i == 0 else CUVE_A_COLOR_START
            end_color = CUVE_B_COLOR_END if i == 0 else CUVE_A_COLOR_END
            gradient_surfaces.append(
                create_gradient_surface(self.width, self.height, start_color, end_color)
            )
        return gradient_surfaces
    
    def _load_background(self):
        """Charge l'image de fond si configurée."""
        if BACKGROUND_IMAGE_PATH:
            try:
                bg_path = os.path.abspath(BACKGROUND_IMAGE_PATH)
                if BACKGROUND_FULL_SCREEN:
                    self.background = create_cover_image(
                        bg_path,
                        self.width,
                        self.height,
                        BACKGROUND_OPACITY
                    )
                else:
                    # Mode carré au-dessus de la question
                    square_size = self.width // 3
                    self.background = create_cover_image(
                        bg_path,
                        square_size,
                        square_size,
                        BACKGROUND_OPACITY,
                        is_circular=True
                    )
                    
                    # Créer une surface de la taille de l'écran
                    background_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    
                    # Calculer la position pour centrer l'image au-dessus de la question
                    x_offset = (self.width - square_size) // 2
                    y_offset = self.height//16
                    
                    # Dessiner l'image centrée sur la surface
                    background_surface.blit(self.background, (x_offset, y_offset))
                    self.background = background_surface
                    
            except Exception as e:
                print(f"Impossible de charger l'image de fond : {BACKGROUND_IMAGE_PATH}")
                print(f"Erreur : {str(e)}")
    
    def draw(self, screen: pygame.Surface, current_gradient: Optional[pygame.Surface] = None, gradient_alpha: int = 0):
        """
        Dessine le fond sur l'écran.
        
        Args:
            screen (pygame.Surface): Surface de l'écran
            current_gradient (Optional[pygame.Surface]): Dégradé actuel
            gradient_alpha (int): Opacité du dégradé
        """
        screen.fill(FOND)
        if self.background:
            screen.blit(self.background, (0, 0))
        
        # Affichage du gradient de victoire
        if current_gradient and gradient_alpha > 0:
            temp_surface = pygame.Surface((self.width, self.height))
            temp_surface.blit(current_gradient, (0, 0))
            temp_surface.set_alpha(gradient_alpha)
            screen.blit(temp_surface, (0, 0)) 