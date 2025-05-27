import pygame
from typing import Tuple, List

def create_gradient_surface(
    width: int,
    height: int,
    start_color: Tuple[int, int, int],
    end_color: Tuple[int, int, int],
    direction: str = "diagonal"
) -> pygame.Surface:
    """
    Crée une surface avec un dégradé de couleurs.
    
    Args:
        width (int): Largeur de la surface
        height (int): Hauteur de la surface
        start_color (Tuple[int, int, int]): Couleur de départ (R, G, B)
        end_color (Tuple[int, int, int]): Couleur de fin (R, G, B)
        direction (str): Direction du dégradé ("diagonal", "horizontal", "vertical")
        
    Returns:
        pygame.Surface: Surface avec le dégradé
    """
    gradient_surface = pygame.Surface((width, height))
    
    for y in range(height):
        for x in range(width):
            if direction == "diagonal":
                # Dégradé diagonal (coin supérieur gauche vers coin inférieur droit)
                distance = (x + y) / (width + height)
            elif direction == "horizontal":
                # Dégradé horizontal (gauche vers droite)
                distance = x / width
            elif direction == "vertical":
                # Dégradé vertical (haut vers bas)
                distance = y / height
            else:
                raise ValueError("Direction invalide. Utilisez 'diagonal', 'horizontal' ou 'vertical'")
            
            # Calculer la couleur interpolée
            color = tuple(
                int(start_color[j] + (end_color[j] - start_color[j]) * distance)
                for j in range(3)
            )
            
            gradient_surface.set_at((x, y), color)
    
    return gradient_surface 