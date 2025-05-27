import pymunk
import pygame
import os
from config import *
from utils.image import create_squared_image
from utils.color import create_gradient_surface

class CuveManager:
    def __init__(self, space):
        self.space = space
        self.cuves = []
        self.counts = [0, 0]  # Compteurs cumulatifs pour chaque cuve
        self.temp_counts = [0, 0]  # Compteurs temporaires pour l'affichage
        self.particles_in_cuves = []  # Liste des particules dans les cuves avec leur temps d'entrée
        self.physics_active = True  # État de la physique
        
        self._initialize_fonts()
        self._create_gradient_surfaces()
        self._load_response_images()

    def _initialize_fonts(self):
        """Initialise les polices de caractères utilisées pour le rendu."""
        self.font = pygame.font.SysFont("Poppins", CUVE_FONT_SIZE, bold=True)
        self.fontCounter = pygame.font.SysFont("Poppins", int(CUVE_FONT_SIZE * 0.8), bold=True)

    def _create_gradient_surfaces(self):
        """Crée les surfaces de dégradé pour les cuves."""
        self.gradient_surfaces = []
        for i in range(2):
            start_color = CUVE_B_COLOR_START if i == 0 else CUVE_A_COLOR_START
            end_color = CUVE_B_COLOR_END if i == 0 else CUVE_A_COLOR_END
            
            gradient_surface = create_gradient_surface(
                CUVE_LARGEUR,
                CUVE_HAUTEUR,
                start_color,
                end_color,
                "diagonal"
            )
            
            self.gradient_surfaces.append(gradient_surface)

    def _load_response_images(self):
        """Charge les images de réponses pour les cuves."""
        imgSize = CUVE_HAUTEUR * 0.6
        self.reponse_a_img = self._load_single_response_image(REPONSE_A_IMAGE_PATH, imgSize)
        self.reponse_b_img = self._load_single_response_image(REPONSE_B_IMAGE_PATH, imgSize)

    def _load_single_response_image(self, image_path, size):
        """Charge une image de réponse individuelle."""
        if not image_path:
            return None
        try:
            return create_squared_image(image_path, size, is_circular=REPONSE_CIRCLE)
        except Exception as e:
            print(f"Impossible de charger l'image : {image_path}")
            print(f"Erreur : {str(e)}")
            return None

    def set_physics_state(self, active):
        """Active ou désactive la physique."""
        self.physics_active = active

    def create_cuve(self, x, color):
        """Crée une cuve à la position x avec la couleur spécifiée."""
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segments = self._create_cuve_segments(body, x)
        
        # Ajouter d'abord le body à l'espace
        self.space.add(body)
        
        # Ensuite ajouter les segments
        for segment in segments:
            segment.friction = CUVE_FRICTION
            segment.color = color
            self.space.add(segment)
        
        rect = (x, HEIGHT - CUVE_HAUTEUR, CUVE_LARGEUR, CUVE_HAUTEUR)
        self.cuves.append((rect, color))

    def _create_cuve_segments(self, body, x):
        """Crée les segments physiques d'une cuve."""
        base = pymunk.Segment(body, (x, HEIGHT), (x + CUVE_LARGEUR, HEIGHT), 4)
        left = pymunk.Segment(body, (x, HEIGHT - CUVE_HAUTEUR), (x, HEIGHT), 4)
        right = pymunk.Segment(body, (x + CUVE_LARGEUR, HEIGHT - CUVE_HAUTEUR), (x + CUVE_LARGEUR, HEIGHT), 4)
        return [base, left, right]

    def update_counts(self, particles):
        """Met à jour les compteurs de particules dans les cuves."""
        self._reset_temp_counts()
        self._update_particle_positions(particles)
        self._check_particles_in_cuves(particles)
        self._remove_expired_particles(particles)

    def _reset_temp_counts(self):
        """Réinitialise les compteurs temporaires."""
        self.temp_counts = [0, 0]

    def _update_particle_positions(self, particles):
        """Met à jour les positions des particules avec effet miroir."""
        for particle in particles:
            pos = particle.body.position
            if pos.x < 0:
                particle.body.position = (WIDTH, pos.y)
            elif pos.x > WIDTH:
                particle.body.position = (0, pos.y)

    def _check_particles_in_cuves(self, particles):
        """Vérifie et compte les particules dans les cuves."""
        for particle in particles:
            pos = particle.body.position
            for i, (rect, _) in enumerate(self.cuves):
                if self._is_particle_in_rect(pos, rect):
                    self._handle_particle_in_cuve(particle, i)
                    break

    def _is_particle_in_rect(self, pos, rect):
        """Vérifie si une particule est dans un rectangle."""
        return (rect[0] <= pos.x <= rect[0] + rect[2] and 
                rect[1] <= pos.y <= rect[1] + rect[3])

    def _handle_particle_in_cuve(self, particle, cuve_index):
        """Gère une particule entrant dans une cuve."""
        if not any(p[0] == particle for p in self.particles_in_cuves):
            self.counts[cuve_index] += 1
            self.particles_in_cuves.append((particle, pygame.time.get_ticks()))
        self.temp_counts[cuve_index] += 1

    def _remove_expired_particles(self, particles):
        """Supprime les particules (formes) qui ont dépassé leur temps de vie."""
        current_time = pygame.time.get_ticks()
        particles_to_delete = []

        for shape, entry_time in self.particles_in_cuves[:]:
            if (current_time - entry_time) / 1000 >= DELAI_DISPARITION:
                if shape in particles:
                    particles_to_delete.append(shape)
                self.particles_in_cuves.remove((shape, entry_time))

        for shape in particles_to_delete:
            try:
                body = shape.body

                # VÉRIFICATION : affiche que tu vas bien retirer
                self.space.remove(shape, body)

                if shape in particles:
                    particles.remove(shape)

            except Exception as e:
                print(f"Erreur lors de la suppression d'une particule: {e}")

    def draw(self, screen):
        """Dessine les cuves et leurs éléments sur l'écran."""
        winner_index = self._get_winner_index()
        
        for i, (rect, _) in enumerate(self.cuves):
            self._draw_cuve_background(screen, rect, i, winner_index)
            self._draw_cuve_content(screen, rect, i, winner_index)

    def _get_winner_index(self):
        """Détermine l'index de la cuve gagnante."""
        if not self.physics_active and self.counts[0] != self.counts[1]:
            return 0 if self.counts[0] > self.counts[1] else 1
        return None

    def _draw_cuve_background(self, screen, rect, index, winner_index):
        """Dessine l'arrière-plan d'une cuve."""
        if not self.physics_active:
            if index == winner_index:
                self._draw_winner_gradient(screen, rect)
            else:
                pygame.draw.rect(screen, GRIS_CUVE, rect)
        else:
            screen.blit(self.gradient_surfaces[index], (rect[0], rect[1]))

    def _draw_winner_gradient(self, screen, rect):
        """Dessine le dégradé pour la cuve gagnante."""
        temp_surface = create_gradient_surface(
            rect[2],
            rect[3],
            BLEU_GAGNANT,
            (0, 50, 150),
            "diagonal"
        )
        screen.blit(temp_surface, (rect[0], rect[1]))

    def _draw_cuve_content(self, screen, rect, index, winner_index):
        """Dessine le contenu d'une cuve (compteur, texte, image)."""
        text_color = self._get_text_color(index, winner_index)
        self._draw_counter(screen, rect, index, text_color)
        self._draw_response_text(screen, rect, index, text_color)
        self._draw_response_image(screen, rect, index)

    def _get_text_color(self, index, winner_index):
        """Détermine la couleur du texte en fonction de l'état du jeu."""
        if not self.physics_active:
            return OR if index == winner_index else GRIS_TEXTE
        return BLANC

    def _draw_counter(self, screen, rect, index, text_color):
        """Dessine le compteur de particules."""
        count_text = self.fontCounter.render(str(self.counts[index]), True, text_color)
        margin = int(WIDTH * 0.02)  # 2% de la largeur de l'écran
        count_x = rect[0] + margin if index == 0 else rect[0] + rect[2] - margin
        count_rect = count_text.get_rect()
        if index == 0:
            count_rect.left = count_x
        else:
            count_rect.right = count_x
        # Centrer verticalement le compteur dans la cuve
        count_rect.centery = rect[1] + rect[3] // 2
        screen.blit(count_text, count_rect)

    def _draw_response_text(self, screen, rect, index, text_color):
        """Dessine le texte de réponse."""
        status_text = REPONSE_B if index == 0 else REPONSE_A
        
        # Déterminer la taille de police en fonction du texte le plus long
        max_text_length = max(len(REPONSE_A), len(REPONSE_B))
        if max_text_length > 20:
            font_size = int(CUVE_FONT_SIZE * 0.6)
        elif max_text_length > 10:
            font_size = int(CUVE_FONT_SIZE * 0.7)
        else:
            font_size = CUVE_FONT_SIZE
            
        temp_font = pygame.font.SysFont("Poppins", font_size, bold=True)
        status = temp_font.render(status_text, True, text_color)
            
        status_rect = status.get_rect(center=(rect[0] + rect[2]//2, rect[1] + 5 + status.get_height()//2))
        screen.blit(status, status_rect)

    def _draw_response_image(self, screen, rect, index):
        """Dessine l'image de réponse si elle existe."""
        response_img = self.reponse_b_img if index == 0 else self.reponse_a_img
        if response_img:
            img_rect = response_img.get_rect()
            img_rect.midbottom = (rect[0] + rect[2]//2, rect[1] + rect[3] - response_img.get_height()//16)
            screen.blit(response_img, img_rect) 