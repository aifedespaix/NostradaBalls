import pygame
from typing import Tuple, Optional
import os

def calculate_cover_size(
    original_size: Tuple[int, int],
    target_width: int,
    target_height: int
) -> Tuple[int, int]:
    """
    Calcule les dimensions pour un redimensionnement de type "cover".
    
    Args:
        original_size (Tuple[int, int]): Dimensions originales (largeur, hauteur)
        target_width (int): Largeur cible
        target_height (int): Hauteur cible
        
    Returns:
        Tuple[int, int]: Nouvelles dimensions (largeur, hauteur)
    """
    screen_ratio = target_width / target_height
    image_ratio = original_size[0] / original_size[1]
    
    if screen_ratio > image_ratio:
        scale = target_width / original_size[0]
        new_width = target_width
        new_height = int(original_size[1] * scale)
    else:
        scale = target_height / original_size[1]
        new_width = int(original_size[0] * scale)
        new_height = target_height
    
    return new_width, new_height

def create_circular_mask(
    target_width: int,
    target_height: int
) -> pygame.Surface:
    """
    Crée un masque circulaire.
    
    Args:
        target_width (int): Largeur cible
        target_height (int): Hauteur cible
        
    Returns:
        pygame.Surface: Surface avec le masque circulaire
    """
    circle_surface = pygame.Surface((target_width, target_width), pygame.SRCALPHA)
    circle_center = (target_width // 2, target_width // 2)
    circle_radius = target_width // 2
    pygame.draw.circle(circle_surface, (255, 255, 255, 255), circle_center, circle_radius)
    return circle_surface

def apply_circular_mask(
    image_surface: pygame.Surface,
    target_width: int,
    target_height: int
) -> pygame.Surface:
    """
    Applique un masque circulaire à une surface.
    
    Args:
        image_surface (pygame.Surface): Surface à masquer
        target_width (int): Largeur cible
        target_height (int): Hauteur cible
        
    Returns:
        pygame.Surface: Surface masquée
    """
    mask = create_circular_mask(target_width, target_height)
    image_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return image_surface

def create_cover_image(
    image_path: str,
    target_width: int,
    target_height: int,
    opacity: float = 1.0,
    is_circular: bool = False
) -> Optional[pygame.Surface]:
    """
    Crée une surface avec une image en mode "cover" (remplit tout l'espace disponible).
    
    Args:
        image_path (str): Chemin vers l'image
        target_width (int): Largeur cible
        target_height (int): Hauteur cible
        opacity (float): Opacité de l'image (0.0 à 1.0)
        is_circular (bool): Si True, l'image sera découpée en cercle
        
    Returns:
        Optional[pygame.Surface]: Surface avec l'image en cover, ou None si erreur
    """
    try:
        # Charger l'image originale
        original = pygame.image.load(image_path).convert_alpha()
        original_size = original.get_size()
        
        # Calculer les nouvelles dimensions
        new_width, new_height = calculate_cover_size(original_size, target_width, target_height)
        
        # Redimensionner l'image
        resized = pygame.transform.smoothscale(original, (new_width, new_height))
        
        if is_circular:
            # Créer une surface pour l'image redimensionnée
            img_surface = pygame.Surface((target_width, target_width), pygame.SRCALPHA)
            
            # Centrer l'image sur la surface
            x_offset = (target_width - new_width) // 2
            y_offset = (target_width - new_height) // 2
            
            # S'assurer que l'image couvre toute la surface
            x_offset = min(0, x_offset)
            y_offset = min(0, y_offset)
            
            img_surface.blit(resized, (x_offset, y_offset))
            
            # Appliquer le masque circulaire
            img_surface = apply_circular_mask(img_surface, target_width, target_height)
            
            # Créer la surface finale
            final_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            final_surface.blit(img_surface, (0, 0))
        else:
            # Créer la surface finale
            final_surface = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            
            # Centrer l'image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            
            final_surface.blit(resized, (x_offset, y_offset))
        
        # Appliquer l'opacité
        final_surface.set_alpha(int(255 * opacity))
        
        return final_surface
        
    except Exception as e:
        print(f"Erreur lors du chargement de l'image {image_path}: {str(e)}")
        return None

def create_squared_image(
    image_path: str,
    size: int,
    is_circular: bool = False,
) -> Optional[pygame.Surface]:
    """
    Crée une image pour une cuve avec les effets visuels appropriés.
    
    Args:
        image_path (str): Chemin vers l'image
        size (int): Taille de l'image
        is_circular (bool): Si True, l'image sera découpée en cercle
        add_border (bool): Si True, ajoute une bordure au cercle
        add_highlight (bool): Si True, ajoute un effet de brillance
        
    Returns:
        Optional[pygame.Surface]: Surface avec l'image et les effets, ou None si erreur
    """
    try:
        # Créer l'image de base en mode cover
        base_surface = create_cover_image(image_path, size, size, 1.0, is_circular)
        if base_surface is None:
            return None
            
        return base_surface
        
    except Exception as e:
        print(f"Erreur lors de la création de l'image de cuve {image_path}: {str(e)}")
        return None 