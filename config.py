# Configuration de la fenêtre
DEBUG = False
TEMPS_LIMITE = 60  # Temps limite de la partie en secondes
RATIO = 0.5 if DEBUG else 1
WIDTH = int(1080 * RATIO)
HEIGHT = int(1920 * RATIO)
FPS = 60
VISUAL = DEBUG

THEME = "semaine"

# Configuration des dossiers de sortie
OUTPUT_DIR = f"output/{THEME}"  # Dossier de sortie basé sur le thème

QUESTION = "Cette semaine, il va t'arriver..."
REPONSE_A = "Une rencontre"
REPONSE_B = "Une perte"

# Configuration de l'image de fond
BACKGROUND_IMAGE_PATH = f"assets/themes/{THEME}/bg.png"  # Chemin vers l'image de fond
BACKGROUND_FULL_SCREEN = True
BACKGROUND_OPACITY = 0.5  # Opacité de l'image de fond (0.0 à 1.0)

# Configuration des particules
PARTICLE_RADIUS = int(6 * RATIO)
EMIT_INTERVAL = 0.2
GOLDEN_PARTICLE_FREQUENCY = 10  # Une balle sur 10 sera en or
PARTICLE_TEXTURE_PATH = None  # Chemin vers l'image de texture des billes (None = pas de texture)

# Configuration de la physique
GRAVITY = (0, 85)
PARTICLE_FRICTION = 0.6
PARTICLE_ELASTICITY = 0.2

# Couleurs
ROUGE = (200, 50, 50)
ROUGE_FONCE = (100, 25, 25)
VERT = (40, 180, 40)
VERT_FONCE = (20, 100, 20)
BLEU = (0, 150, 255)
GRIS = (200, 200, 200)
FOND = (30, 30, 30)
BLANC = (255, 255, 255)
BEIGE_JAUNE = (232, 200, 100)
BEIGE_JAUNE_FONCE = (208, 180, 90)
NOIR_DOUX = (47, 47, 47)
NOIR_DOUX_FONCE = (38, 38, 38)

CUVE_A_COLOR_START = (255, 210, 150)   
CUVE_A_COLOR_END   = (180, 80, 200)    
CUVE_B_COLOR_START = (120, 140, 255)   
CUVE_B_COLOR_END   = (60, 60, 80)      

# Configuration de la musique de fond
BACKGROUND_MUSIC_PATH = f"assets/themes/{THEME}/music.wav"  # Chemin vers la musique de fond
BACKGROUND_MUSIC_VOLUME = 0.6

# Configuration de la question
QUESTION_SOUND_PATH = f"assets/themes/{THEME}/question.wav"
QUESTION_FONT_SIZE = int(64 * RATIO)  # Taille de police plus grande pour la question
QUESTION_COLOR = (255, 255, 255)  # Couleur blanche pour la question
QUESTION_POSITION = (WIDTH // 2, HEIGHT // 3)  # Position centrée à 1/3 de la hauteur
QUESTION_BG_COLOR = (0, 0, 0, 180)  # Fond noir avec opacité 80

# Configuration des réponses
REPONSE_CIRCLE = True
REPONSE_A_IMAGE_PATH = f"assets/themes/{THEME}/a.png"  # ou None si pas d'image
REPONSE_A_VOICE_PATH = f"assets/themes/{THEME}/a.wav"
REPONSE_A_COLOR = ROUGE

REPONSE_B_IMAGE_PATH = f"assets/themes/{THEME}/b.png"  # ou None si pas d'image
REPONSE_B_VOICE_PATH = f"assets/themes/{THEME}/b.wav"
REPONSE_B_COLOR = VERT

# Configuration de la réponse
REPONSE_FONT_SIZE = int(80 * RATIO)  # Taille de police plus grande pour la réponse
REPONSE_POSITION = (WIDTH // 2, HEIGHT // 2)  # Position exactement au centre de l'écran
REPONSE_ZOOM_MIN = 1.0  # Échelle minimale du zoom
REPONSE_ZOOM_MAX = 1.6  # Échelle maximale du zoom
REPONSE_ZOOM_SPEED = 0.5  # Vitesse du zoom

# Configuration des obstacles
OBSTACLE_FRICTION = 2
OBSTACLE_ELASTICITY = 0.2
NUM_OBSTACLES = int(32 * RATIO) # Nombre total d'obstacles
NUM_CIRCLES = int(20 * RATIO)     # Nombre de cercles
NUM_ROTATING = int(18 * RATIO)       # Nombre d'obstacles rotatifs
NUM_PIVOT = int(22 * RATIO)        # Nombre de barres pivotantes

# Configuration des cuves
CUVE_FRICTION = 0.5
CUVE_HAUTEUR = int(250 * RATIO)
CUVE_LARGEUR = WIDTH // 2  # Chaque cuve occupe la moitié de la largeur de l'écran
CUVE_FONT_SIZE = int(60 * RATIO)

# Configuration du jeu
SEUIL_VICTOIRE = 1  # Seuil à atteindre pour gagner (multiple de 100)
DELAI_DISPARITION = 25  # Délai en secondes avant la disparition des billes dans les cuves
DELAI_ARRET = 3  # Délai en secondes avant l'arrêt complet du jeu après l'arrêt de la physique
WINNER = None  # Le gagnant attendu ("A" ou "B")

# Couleurs pour les cuves (fin de partie)
GRIS_CUVE = (100, 100, 100)
BLEU_GAGNANT = (0, 100, 255)
GRIS_TEXTE = (180, 180, 180)
OR = (255, 215, 0)
