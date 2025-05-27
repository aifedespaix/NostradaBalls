import pygame
import os
from typing import Optional
from utils.image import create_squared_image
from config import *
import math

class Response:
    """Gestionnaire de l'affichage des réponses."""
    
    def __init__(self, width: int, height: int):
        """
        Initialise l'affichage des réponses.
        
        Args:
            width (int): Largeur de l'écran
            height (int): Hauteur de l'écran
        """
        self.width = width
        self.height = height
        self.zoom_time = 0
        self.reponse = None
        self.font = pygame.font.SysFont("Poppins", REPONSE_FONT_SIZE, bold=True)
        self._load_response_images()
    
    def _load_response_images(self):
        """Charge les images des réponses."""
        imgSize = int(self.width // 3)  # Conversion explicite en int
        self.reponse_a_img = None
        self.reponse_b_img = None
        
        if REPONSE_A_IMAGE_PATH:
            try:
                self.reponse_a_img = create_squared_image(REPONSE_A_IMAGE_PATH, imgSize, is_circular=REPONSE_CIRCLE)
            except Exception as e:
                print(f"Impossible de charger l'image de la réponse A : {REPONSE_A_IMAGE_PATH}")
                print(f"Erreur : {str(e)}")
                
        if REPONSE_B_IMAGE_PATH:
            try:
                self.reponse_b_img = create_squared_image(REPONSE_B_IMAGE_PATH, imgSize, is_circular=REPONSE_CIRCLE)
            except Exception as e:
                print(f"Impossible de charger l'image de la réponse B : {REPONSE_B_IMAGE_PATH}")
                print(f"Erreur : {str(e)}")

    
    def load_response_image(image_path: str, size: int) -> Optional[pygame.Surface]:
        """
        Charge et prépare une image de réponse.
        
        Args:
            image_path (str): Chemin vers l'image
            size (int): Taille souhaitée de l'image
            
        Returns:
            Optional[pygame.Surface]: Surface pygame avec l'image chargée, ou None si erreur
        """
        try:
            return create_squared_image(image_path, size, is_circular=VISUAL)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de réponse {image_path}: {str(e)}")
            return None

    
    def update(self, dt: float):
        """
        Met à jour l'animation de la réponse.
        
        Args:
            dt (float): Pas de temps
        """
        self.zoom_time += dt * REPONSE_ZOOM_SPEED
    
    def set_response(self, reponse: str):
        """
        Définit la réponse à afficher.
        
        Args:
            reponse (str): La réponse à afficher
        """
        self.reponse = reponse
    
    def draw(self, screen: pygame.Surface):
        """
        Dessine la réponse sur l'écran.
        
        Args:
            screen (pygame.Surface): Surface de l'écran
        """
        if self.reponse:
            # Calcul de l'échelle de zoom
            zoom_scale = REPONSE_ZOOM_MIN + (REPONSE_ZOOM_MAX - REPONSE_ZOOM_MIN) * (
                1 - math.cos(self.zoom_time * REPONSE_ZOOM_SPEED)
            ) / 2

            # Création du texte de réponse
            reponse_text = self.font.render(self.reponse, True, BLANC)
            reponse_rect = reponse_text.get_rect(center=REPONSE_POSITION)

            # Dessiner le texte avec l'effet de zoom
            screen.blit(reponse_text, reponse_rect)

            # Afficher l'image sous la réponse si elle existe
            img = None
            if self.reponse == REPONSE_A and self.reponse_a_img:
                img = self.reponse_a_img
            elif self.reponse == REPONSE_B and self.reponse_b_img:
                img = self.reponse_b_img
                
            if img:
                img_rect = img.get_rect(midtop=(REPONSE_POSITION[0], reponse_rect.bottom + 20))
                screen.blit(img, img_rect) 