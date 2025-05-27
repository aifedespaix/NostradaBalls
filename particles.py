import pymunk
import random
import math
from config import *
import pygame

class ParticleManager:
    def __init__(self, space):
        self.space = space
        self.particles = []
        self.spawn_time = 0
        self.spawn_amplitude = 200  # Amplitude de l'oscillation
        self.spawn_frequency = 2  # Fréquence de l'oscillation
        self.particle_count = 0  # Compteur pour les balles en or
        
        # Chargement de la texture si spécifiée
        self.texture = None
        if PARTICLE_TEXTURE_PATH:
            try:
                # Charger l'image
                texture = pygame.image.load(PARTICLE_TEXTURE_PATH)
                # Redimensionner l'image à la taille de la particule
                texture_size = PARTICLE_RADIUS * 2
                self.texture = pygame.transform.smoothscale(texture, (texture_size, texture_size))
            except:
                print(f"Impossible de charger la texture: {PARTICLE_TEXTURE_PATH}")
                self.texture = None

    def emit_particle(self):
        x = WIDTH // 2 + self.spawn_amplitude * math.sin(self.spawn_time * self.spawn_frequency)
        y = 50

        # Déterminer si c'est une balle en or
        self.particle_count += 1
        is_golden = (self.particle_count % GOLDEN_PARTICLE_FREQUENCY) == 0
        mass = 3 if is_golden else 1

        body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, PARTICLE_RADIUS))
        body.position = x, y
        shape = pymunk.Circle(body, PARTICLE_RADIUS)
        shape.friction = PARTICLE_FRICTION
        shape.elasticity = PARTICLE_ELASTICITY
        shape.data = {"is_golden": is_golden}

        self.space.add(body, shape)
        self.particles.append(shape)

        self.spawn_time += 0.1


    def draw(self, screen):
        for shape in self.particles:
            pos = shape.body.position
            velocity = shape.body.velocity
            speed = math.sqrt(velocity.x**2 + velocity.y**2)
            
            # Supprimer la balle si elle va trop vite (plus de 1000 unités)
            if speed > 5000:
                print(f"Balle supprimée - Célérité excessive: {speed:.2f} unités/s")
                self.space.remove(shape)
                self.space.remove(shape.body)
                self.particles.remove(shape)
                continue
            
            # S'assurer que la position est dans les limites de l'écran
            x = max(0, min(WIDTH, pos[0]))
            y = max(0, min(HEIGHT, pos[1]))
            
            if shape.data["is_golden"]:
                # Couleur dorée pour les balles en or
                r, g, b = OR
            else:
                # Variation de couleur bleue basée sur la vitesse et la position
                base_blue = 200  # Bleu de base
                speed_factor = min(1.0, speed / 500)  # Normalisation de la vitesse
                position_factor = (y / HEIGHT)  # Facteur basé sur la position Y
                
                # Calcul des composantes de couleur avec limitation à 255
                r = min(255, max(0, int(100 + speed_factor * 50)))  # Rouge légèrement variable
                g = min(255, max(0, int(150 + speed_factor * 50)))  # Vert légèrement variable
                b = min(255, max(0, int(base_blue + position_factor * 55)))  # Bleu variable selon la position
            
            # Effet de lueur basé sur la vitesse
            glow_intensity = min(255, max(0, int(speed * 2)))
            
            # Créer une surface pour l'effet de lueur
            glow_size = PARTICLE_RADIUS * 4
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Dessiner plusieurs cercles concentriques pour l'effet de lueur
            center = glow_size // 2
            for radius in range(PARTICLE_RADIUS * 2, 0, -1):
                alpha = min(255, max(0, int(glow_intensity * (radius / (PARTICLE_RADIUS * 2)))))
                color = (r, g, b, alpha)
                pygame.draw.circle(glow_surf, color, (center, center), radius)
            
            # Calculer la position de la lueur en s'assurant qu'elle reste dans les limites
            glow_x = int(x - center)
            glow_y = int(y - center)
            
            # Vérifier si la lueur est visible à l'écran
            if (glow_x + glow_size > 0 and glow_x < WIDTH and 
                glow_y + glow_size > 0 and glow_y < HEIGHT):
                screen.blit(glow_surf, (glow_x, glow_y))
            
            # Effet de brillance (point lumineux)
            highlight_radius = int(PARTICLE_RADIUS * 0.2)  # Réduction de 0.3 à 0.2 pour un point plus fin
            highlight_x = int(x - highlight_radius)
            highlight_y = int(y - highlight_radius)
            
            if (highlight_x + highlight_radius * 2 > 0 and highlight_x < WIDTH and 
                highlight_y + highlight_radius * 2 > 0 and highlight_y < HEIGHT):
                pygame.draw.circle(screen, (255, 255, 255, 200), 
                                 (highlight_x + highlight_radius, 
                                  highlight_y + highlight_radius), 
                                 highlight_radius)
            
            # Particule principale avec dégradé ou texture
            if self.texture:
                # Calculer la position pour centrer la texture
                texture_x = int(x - PARTICLE_RADIUS)
                texture_y = int(y - PARTICLE_RADIUS)
                
                # Créer une surface pour la texture avec alpha
                texture_surf = pygame.Surface((PARTICLE_RADIUS * 1.2, PARTICLE_RADIUS * 1.2), pygame.SRCALPHA)
                
                # Appliquer la texture
                texture_surf.blit(self.texture, (0, 0))
                
                # Appliquer la couleur de base avec alpha
                color_surf = pygame.Surface((PARTICLE_RADIUS * 2, PARTICLE_RADIUS * 2), pygame.SRCALPHA)
                color = OR if shape.data["is_golden"] else (r, g, b)
                pygame.draw.circle(color_surf, (*color, 200),  # Augmentation de l'alpha de 128 à 200
                                 (PARTICLE_RADIUS, PARTICLE_RADIUS), PARTICLE_RADIUS)
                
                # Fusionner la texture et la couleur
                texture_surf.blit(color_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                # Dessiner la texture
                screen.blit(texture_surf, (texture_x, texture_y))
            else:
                # Dessin normal sans texture
                for radius in range(PARTICLE_RADIUS, 0, -1):
                    alpha = min(255, max(0, 255 - int((radius / PARTICLE_RADIUS) * 50)))  # Réduction de la transparence
                    # Variation de couleur dans le dégradé avec limitation
                    r_grad = min(255, max(0, int(r * (1 - radius/PARTICLE_RADIUS * 0.3))))
                    g_grad = min(255, max(0, int(g * (1 - radius/PARTICLE_RADIUS * 0.3))))
                    b_grad = min(255, max(0, int(b * (1 - radius/PARTICLE_RADIUS * 0.3))))
                    color = (r_grad, g_grad, b_grad, alpha)
                    pygame.draw.circle(screen, color, (int(x), int(y)), radius)
            
            # Contour brillant avec couleur variable (limité à 255)
            pygame.draw.circle(screen, (min(255, max(0, r + 20)),  # Réduction de l'intensité du contour
                                      min(255, max(0, g + 20)), 
                                      min(255, max(0, b + 20))), 
                             (int(x), int(y)), 
                             PARTICLE_RADIUS + 1, 1)  # Ajout de +1 pour un contour plus fin 