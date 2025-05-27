import pygame
from typing import List
from utils.text import render_multiline_text
from config import *

class Question:
    """Gestionnaire de l'affichage de la question."""
    
    def __init__(self, width: int, height: int):
        """
        Initialise l'affichage de la question.
        
        Args:
            width (int): Largeur de l'écran
            height (int): Hauteur de l'écran
        """
        self.width = width
        self.height = height
        self.question_zoom_time = 0
        self.font = pygame.font.SysFont("Poppins", QUESTION_FONT_SIZE)
    
    def update(self, dt: float):
        """
        Met à jour l'animation de la question.
        
        Args:
            dt (float): Pas de temps
        """
        if self.question_zoom_time < 3.0:
            self.question_zoom_time += dt
    
    def draw(self, screen: pygame.Surface):
        """
        Dessine la question sur l'écran.
        
        Args:
            screen (pygame.Surface): Surface de l'écran
        """
        # Calcul de l'échelle de zoom pour la question (0.8 à 1.0 sur 3 secondes)
        if self.question_zoom_time < 3.0:
            question_zoom_scale = 0.8 + (0.2 * (self.question_zoom_time / 3.0))
        else:
            question_zoom_scale = 1.0
        
        # Calculer la largeur maximale (80% de la largeur de l'écran)
        max_width = int(self.width * 0.8)
        
        # Rendre le texte sur plusieurs lignes
        question_surfaces = render_multiline_text(QUESTION, self.font, QUESTION_COLOR, max_width)
        
        # Calculer la hauteur totale du texte
        total_height = sum(surface.get_height() for surface in question_surfaces)
        
        # Créer la surface de fond
        bg_surf = pygame.Surface((max_width + 40, total_height + 40), pygame.SRCALPHA)
        bg_surf.fill(QUESTION_BG_COLOR)
        bg_rect = bg_surf.get_rect(center=QUESTION_POSITION)
        
        # Dessiner le fond
        screen.blit(bg_surf, bg_rect)
        
        # Dessiner chaque ligne de texte
        y_offset = bg_rect.top + 20
        for surface in question_surfaces:
            # Appliquer le zoom à la surface
            scaled_surface = pygame.transform.smoothscale(
                surface,
                (int(surface.get_width() * question_zoom_scale),
                 int(surface.get_height() * question_zoom_scale))
            )
            
            # Centrer horizontalement
            x = bg_rect.centerx - scaled_surface.get_width() // 2
            screen.blit(scaled_surface, (x, y_offset))
            y_offset += scaled_surface.get_height() 