import random
import math
from config import *

def setup_scene(space):
    """Configure la scène avec les obstacles et les cuves"""
    from obstacles import ObstacleManager
    from cuves import CuveManager

    obstacle_manager = ObstacleManager(space)
    cuve_manager = CuveManager(space)

    # Initialiser les gestionnaires de collision
    obstacle_manager.setup_collision_handlers()

    # Liste pour stocker les positions des obstacles
    obstacle_positions = []
    circle_positions = []
    min_distance = 20  # Distance minimale entre les obstacles
    min_circle_distance = 80

    def generate_random_position(is_circle=False, side=None):
        """Génère une position aléatoire valide pour un obstacle
        side: 'left' ou 'right' pour spécifier la partie de l'écran"""
        max_attempts = 50
        for _ in range(max_attempts):
            # Créer une grille virtuelle pour une meilleure répartition
            grid_size = 6
            cell_width = WIDTH // grid_size
            
            # Calculer la zone de jeu disponible en tenant compte des marges
            top_margin = CUVE_HAUTEUR  # Marge en haut
            bottom_margin = CUVE_HAUTEUR + 40  # Marge en bas (cuve + espace)
            available_height = HEIGHT - top_margin - bottom_margin
            cell_height = available_height // grid_size
            
            # Sélectionner une cellule aléatoire
            if side == 'left':
                cell_x = random.randint(0, grid_size // 2 - 1)
            elif side == 'right':
                cell_x = random.randint(grid_size // 2, grid_size - 1)
            else:
                cell_x = random.randint(0, grid_size - 1)
                
            cell_y = random.randint(0, grid_size - 1)
            
            # Générer une position aléatoire dans la cellule
            x = cell_x * cell_width + random.randint(20, cell_width - 20)
            y = top_margin + cell_y * cell_height + random.randint(20, cell_height - 20)
            
            if is_valid_position(x, y, is_circle):
                return x, y
        return None

    def is_valid_position(x, y, is_circle=False):
        """Vérifie si la position est suffisamment éloignée des autres obstacles"""
        # Vérifier que l'obstacle n'est pas trop bas
        min_height = HEIGHT - CUVE_HAUTEUR - 40
        if y > min_height:
            return False
            
        # Vérifier que l'obstacle n'est pas trop haut
        if y < CUVE_HAUTEUR:
            return False
            
        # Vérifier la distance avec les autres obstacles
        for pos in obstacle_positions:
            dx = x - pos[0]
            dy = y - pos[1]
            if math.sqrt(dx*dx + dy*dy) < min_distance:
                return False
        
        # Vérifier la distance avec les cercles
        for pos in circle_positions:
            dx = x - pos[0]
            dy = y - pos[1]
            if math.sqrt(dx*dx + dy*dy) < min_circle_distance:
                return False
        
        # Si c'est un cercle, vérifier aussi avec les autres cercles
        if is_circle:
            for pos in circle_positions:
                dx = x - pos[0]
                dy = y - pos[1]
                if math.sqrt(dx*dx + dy*dy) < min_distance:
                    return False
        
        return True

    # Entonnoir central (gardé pour l'entrée)
    entonnoir_x = WIDTH // 2
    entonnoir_y = HEIGHT // 6
    entonnoir_radius = 120
    # obstacle_manager.create_entonnoir((entonnoir_x, entonnoir_y), entonnoir_radius)
    obstacle_positions.append((entonnoir_x, entonnoir_y))

    # Génération aléatoire des obstacles
    num_obstacles = NUM_OBSTACLES  # Nombre total d'obstacles
    num_circles = NUM_CIRCLES     # Nombre de cercles
    num_rotating = NUM_ROTATING    # Nombre d'obstacles rotatifs
    num_pivot = NUM_PIVOT       # Nombre de barres pivotantes

    # Créer les obstacles normaux
    for i in range(num_obstacles):
        side = 'left' if i < num_obstacles // 2 else 'right'
        pos = generate_random_position(side=side)
        if pos:
            x, y = pos
            length = random.randint(80, 150)
            
            # Un obstacle sur trois est plat
            if i % 3 == 0:
                angle = 0  # Angle plat
            else:
                # Angle entre -45 et 45 degrés
                angle = random.uniform(-math.pi/4, math.pi/4)
            
            x2 = x + length * math.cos(angle)
            y2 = y + length * math.sin(angle)
            obstacle_manager.create_obstacle((x, y), (x2, y2))
            obstacle_positions.extend([(x, y), (x2, y2)])

    # Créer les cercles
    for i in range(num_circles):
        side = 'left' if i < num_circles // 2 else 'right'
        pos = generate_random_position(is_circle=True, side=side)
        if pos:
            x, y = pos
            radius = random.randint(20, 30)
            obstacle_manager.create_circular_obstacle((x, y), radius)
            circle_positions.append((x, y))

    # Créer les obstacles rotatifs
    for i in range(num_rotating):
        side = 'left' if i < num_rotating // 2 else 'right'
        pos = generate_random_position(side=side)
        if pos:
            x, y = pos
            length = random.randint(60, 100)
            speed = random.uniform(-3.0, 3.0)
            obstacle_manager.create_rotating_obstacle((x, y), length, speed)

    # Créer les barres pivotantes
    for i in range(num_pivot):
        side = 'left' if i < num_pivot // 2 else 'right'
        pos = generate_random_position(side=side)
        if pos:
            x, y = pos
            length = random.randint(80, 120)
            mass = random.uniform(1.0, 2.0)
            obstacle_manager.create_pivot_bar((x, y), length, mass=mass)
            obstacle_positions.append((x, y))

    obstacle_manager.create_floor()

    # Création des cuves
    cuve_manager.create_cuve(WIDTH // 2, ROUGE)  # Première cuve à droite
    cuve_manager.create_cuve(0, VERT)  # Deuxième cuve à gauche

    return obstacle_manager, cuve_manager 