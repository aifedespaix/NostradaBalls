import pymunk
import math
import pygame
import random
from config import *
from core.audio import AudioManager
from core.time import TimeManager

class SoundManager:
    def __init__(self):
        self.audio_manager = AudioManager()
        self.time_manager = TimeManager()
        self.last_play_time = {}  # Pour le cooldown
        self.cooldown = 0.1  # 100ms de cooldown
    
    def play_sound(self, sound_name):
        """Joue un son par son nom avec un système de cooldown"""
        current_time = self.time_manager.get_current_state().physics_seconds
        
        # Ne pas jouer de son si la physique n'est plus active
        if not self.time_manager.physics_active:
            return
            
        # Vérifier si le son peut être joué (cooldown)
        if sound_name in self.last_play_time:
            if current_time - self.last_play_time[sound_name] < self.cooldown:
                return  # Ne pas jouer le son si le cooldown n'est pas terminé
        
        self.audio_manager.play_sound(sound_name)
        self.last_play_time[sound_name] = current_time

class ObstacleManager:
    def __init__(self, space):
        self.space = space
        self.shapes = []
        self.rotating_shapes = []  # Liste des formes qui tournent
        self.pivot_joints = []  # Liste des joints de pivot
        self.pivot_bars = []  # Liste des barres pivotantes
        # Zone protégée pour la question
        self.question_zone_width = 800  # Largeur de la zone protégée
        self.question_zone_height = 100  # Hauteur de la zone protégée
        self.sound_manager = SoundManager()
        # Limites de vitesse pour les barres pivotantes
        self.max_angular_velocity = 5.0  # Vitesse angulaire maximale
        self.max_linear_velocity = 300.0  # Vitesse linéaire maximale
        # Animation des obstacles circulaires
        self.circular_animations = {}  # Dictionnaire pour stocker les animations
        # Épaisseur des barres
        self.BAR_THICKNESS = 4  # Épaisseur uniforme pour toutes les barres

    def is_in_question_zone(self, position):
        """Vérifie si une position est dans la zone horizontale de la question"""
        x, y = position
        question_x, question_y = QUESTION_POSITION
        
        # Vérifie si la position est dans le rectangle horizontal
        in_x_range = abs(x - question_x) < self.question_zone_width / 2
        in_y_range = abs(y - question_y) < self.question_zone_height / 2
        
        return in_x_range and in_y_range

    def create_pivot_bar(self, position, length, mass=1.0):
        """Crée une barre amovible avec un point de pivot central"""
        if self.is_in_question_zone(position):
            return
        moment = pymunk.moment_for_segment(mass, (-length/2, 0), (length/2, 0), 6)
        body = pymunk.Body(mass, moment)
        body.position = position
        
        shape = pymunk.Segment(body, (-length/2, 0), (length/2, 0), self.BAR_THICKNESS)
        shape.friction = 0.9
        shape.elasticity = 0.5
        shape.color = (100, 200, 255)
        shape.collision_type = 1
        shape.sound_name = 'A'  # Son A pour les barres pivotantes
        
        pivot = pymunk.PivotJoint(self.space.static_body, body, position)
        pivot.collide_bodies = False
        
        self.space.add(body, shape, pivot)
        self.shapes.append(shape)
        self.pivot_joints.append(pivot)
        self.pivot_bars.append(body)

    def create_entonnoir(self, position, radius, segments=60):
        if self.is_in_question_zone(position):
            return  # Ne crée pas l'obstacle s'il est dans la zone de la question
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shapes = []
        for i in range(segments):
            angle1 = math.pi + (i / segments) * math.pi
            angle2 = math.pi + ((i + 1) / segments) * math.pi
            p1 = (position[0] + math.cos(angle1) * radius,
                  position[1] + math.sin(angle1) * radius)
            p2 = (position[0] + math.cos(angle2) * radius,
                  position[1] + math.sin(angle2) * radius)
            segment = pymunk.Segment(body, p1, p2, self.BAR_THICKNESS)
            segment.friction = 0.9
            segment.elasticity = 0.2
            shapes.append(segment)
        self.space.add(body, *shapes)
        self.shapes.extend(shapes)

    def create_rotating_obstacle(self, position, length, rotation_speed=2.0):
        """Crée une barre qui tourne sur elle-même de manière continue"""
        if self.is_in_question_zone(position):
            return
            
        # Vérifier que les points finaux de la barre ne dépassent pas la hauteur minimale
        min_height = HEIGHT - CUVE_HAUTEUR - 40  # 40px de marge
        x, y = position
        
        # Calculer les points finaux de la barre
        p1 = (x - length/2, y)
        p2 = (x + length/2, y)
        
        # Si l'un des points est trop bas, on ne crée pas l'obstacle
        if p1[1] > min_height or p2[1] > min_height:
            return
            
        # Créer un corps cinématique pour la barre (peut tourner mais pas être affecté par la physique)
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        body.position = position
        
        # Créer la forme de la barre
        shape = pymunk.Segment(body, (-length/2, 0), (length/2, 0), self.BAR_THICKNESS)
        shape.friction = 1.0
        shape.elasticity = 0.8
        shape.color = (200, 100, 100)
        shape.collision_type = 2
        shape.sound_name = 'A'
        
        # Ajouter le corps et la forme à l'espace
        self.space.add(body, shape)
        self.shapes.append(shape)
        
        # Définir une vitesse de rotation aléatoire (gauche ou droite)
        direction = 1 if random.random() > 0.5 else -1
        rotation_speed = rotation_speed * direction
        
        # Ajouter à la liste des formes rotatives
        self.rotating_shapes.append((body, rotation_speed))

    def create_circular_obstacle(self, position, radius):
        """Crée un obstacle circulaire avec un effet de rebond élastique"""
        if self.is_in_question_zone(position):
            return
            
        # Vérifier que l'obstacle ne dépasse pas la hauteur minimale
        min_height = HEIGHT - CUVE_HAUTEUR - 40  # 40px de marge
        x, y = position
        
        # Si le point le plus bas du cercle dépasse la hauteur minimale, on ne crée pas l'obstacle
        if y + radius > min_height:
            return
            
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Circle(body, radius)
        shape.friction = 0.01
        shape.elasticity = 4.0
        shape.color = (255, 200, 100)
        shape.collision_type = 3
        shape.sound_name = 'B'  # Son B pour les obstacles circulaires
        body.position = position
        self.space.add(body, shape)
        self.shapes.append(shape)
        # Initialiser l'animation pour cet obstacle
        self.circular_animations[shape] = {
            'scale': 1.0,
            'target_scale': 1.0,
            'animation_speed': 0.2
        }

    def create_obstacle(self, p1, p2):
        """Crée un obstacle statique normal"""
        if self.is_in_question_zone(p1) or self.is_in_question_zone(p2):
            return
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, p1, p2, self.BAR_THICKNESS)
        shape.friction = OBSTACLE_FRICTION
        shape.elasticity = OBSTACLE_ELASTICITY
        shape.collision_type = 4  # Type de collision pour les obstacles normaux
        self.space.add(body, shape)
        self.shapes.append(shape)

    def create_floor(self):
        # Création du plancher
        floor = pymunk.Segment(self.space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), 10)
        floor.friction = 1
        self.space.add(floor)
        self.shapes.append(floor)

        # Création du plafond invisible
        ceiling = pymunk.Segment(self.space.static_body, (0, 0), (WIDTH, 0), 1)
        ceiling.friction = 0.1
        ceiling.elasticity = 0.5
        self.space.add(ceiling)
        self.shapes.append(ceiling)

    def update(self, dt):
        """Met à jour la rotation des barres et limite leur vitesse"""
        # Mise à jour des barres rotatives
        for body, speed in self.rotating_shapes:
            body.angle += speed * dt

        # Limitation de la vitesse des barres pivotantes
        for body in self.pivot_bars:
            # Limitation de la vitesse angulaire
            if abs(body.angular_velocity) > self.max_angular_velocity:
                body.angular_velocity = self.max_angular_velocity * (1 if body.angular_velocity > 0 else -1)
            
            # Limitation de la vitesse linéaire
            velocity = body.velocity
            speed = (velocity.x * velocity.x + velocity.y * velocity.y) ** 0.5
            if speed > self.max_linear_velocity:
                factor = self.max_linear_velocity / speed
                body.velocity = velocity.x * factor, velocity.y * factor

        # Mise à jour des animations des obstacles circulaires
        for shape, anim in self.circular_animations.items():
            if anim['scale'] != anim['target_scale']:
                # Animation de retour à la taille normale
                anim['scale'] += (anim['target_scale'] - anim['scale']) * anim['animation_speed']
                if abs(anim['scale'] - anim['target_scale']) < 0.01:
                    anim['scale'] = anim['target_scale']

    def draw(self, screen):
        # Dessiner les formes
        for shape in self.shapes:
            if isinstance(shape, pymunk.Segment):
                # Pour les segments rotatifs ou amovibles, on utilise la position et l'angle du corps
                if shape.body.body_type in (pymunk.Body.KINEMATIC, pymunk.Body.DYNAMIC):
                    pos = shape.body.position
                    angle = shape.body.angle
                    length = (shape.b - shape.a).length
                    # Calculer les points finaux en tenant compte de la rotation
                    p1 = (pos.x + math.cos(angle) * (-length/2), pos.y + math.sin(angle) * (-length/2))
                    p2 = (pos.x + math.cos(angle) * (length/2), pos.y + math.sin(angle) * (length/2))
                else:
                    p1 = shape.a
                    p2 = shape.b
                color = getattr(shape, "color", GRIS)
                # Utiliser l'épaisseur de la barre pour le rendu
                pygame.draw.line(screen, color, p1, p2, self.BAR_THICKNESS)
            elif isinstance(shape, pymunk.Circle):
                pos = shape.body.position
                radius = shape.radius
                color = getattr(shape, "color", GRIS)
                
                # Appliquer l'effet d'animation si l'obstacle est dans le dictionnaire d'animations
                if shape in self.circular_animations:
                    anim = self.circular_animations[shape]
                    radius = int(radius * anim['scale'])
                
                # Dessiner un cercle plein anti-aliased
                pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), radius)

    def setup_collision_handlers(self):
        """Configure les gestionnaires de collision"""
        def handle_collision(arbiter, space, data):
            # Ne pas traiter les collisions si la physique n'est plus active
            if not self.sound_manager.time_manager.physics_active:
                return True
                
            shape1, shape2 = arbiter.shapes
            
            # Gérer l'animation des obstacles circulaires
            for shape in [shape1, shape2]:
                if isinstance(shape, pymunk.Circle) and shape in self.circular_animations:
                    anim = self.circular_animations[shape]
                    anim['scale'] = 1.3  # Agrandissement initial
                    anim['target_scale'] = 1.0  # Retour à la taille normale
            
            # Ne jouer le son que si au moins un des objets est un obstacle spécial (type 1, 2, 3)
            # et qu'aucun n'est un obstacle normal (type 4)
            if ((shape1.collision_type in [1, 2, 3] or shape2.collision_type in [1, 2, 3]) and
                shape1.collision_type != 4 and shape2.collision_type != 4):
                # Jouer le son approprié
                if hasattr(shape1, 'sound_name') and shape1.sound_name:
                    self.sound_manager.play_sound(shape1.sound_name)
                elif hasattr(shape2, 'sound_name') and shape2.sound_name:
                    self.sound_manager.play_sound(shape2.sound_name)
            
            return True

        def prevent_rotation(arbiter, space, data):
            pivot_bar = arbiter.shapes[0].body
            # Limitation immédiate de la vitesse angulaire lors de la collision
            if abs(pivot_bar.angular_velocity) > self.max_angular_velocity:
                pivot_bar.angular_velocity = self.max_angular_velocity * (1 if pivot_bar.angular_velocity > 0 else -1)
            return True

        # Ajout des gestionnaires de collision avec sons pour tous les types d'obstacles
        # Collision entre billes et obstacles normaux (type 0)
        self.space.add_collision_handler(0, 1).separate = handle_collision  # Bille avec barre pivotante
        self.space.add_collision_handler(0, 2).separate = handle_collision  # Bille avec obstacle rotatif
        self.space.add_collision_handler(0, 3).separate = handle_collision  # Bille avec obstacle circulaire
        self.space.add_collision_handler(0, 4).separate = handle_collision  # Bille avec obstacle normal

        # Collisions entre obstacles
        self.space.add_collision_handler(1, 2).separate = handle_collision  # Barre pivotante avec obstacle rotatif
        self.space.add_collision_handler(1, 3).separate = handle_collision  # Barre pivotante avec obstacle circulaire
        self.space.add_collision_handler(2, 3).separate = handle_collision  # Obstacle rotatif avec obstacle circulaire 