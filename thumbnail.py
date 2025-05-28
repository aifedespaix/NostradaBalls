from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from config import (
    QUESTION, REPONSE_A, REPONSE_B, REPONSE_A_IMAGE_PATH, REPONSE_B_IMAGE_PATH,
    CUVE_A_COLOR_START, CUVE_B_COLOR_START, OUTPUT_DIR, THEME
)

# Constantes
WIDTH, HEIGHT = 1080, 1920
LOGO_SIZE = WIDTH // 3  # 360px
MARGIN = 40

# Chemins
BASE_IMAGE_PATH = "assets/thumnail/base.png"  # À placer à la racine ou adapter le chemin
OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"thumbnail-{THEME}.png")

# S'assurer que le dossier de sortie existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonctions utilitaires
def load_logo(path):
    try:
        img = Image.open(path).convert("RGBA")
        # Redimension cover carré
        ratio = max(LOGO_SIZE / img.width, LOGO_SIZE / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
        # Crop carré centré
        left = (img.width - LOGO_SIZE) // 2
        top = (img.height - LOGO_SIZE) // 2
        img = img.crop((left, top, left + LOGO_SIZE, top + LOGO_SIZE))
        
        # Créer un masque circulaire
        mask = Image.new('L', (LOGO_SIZE, LOGO_SIZE), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, LOGO_SIZE, LOGO_SIZE), fill=255)
        
        # Appliquer le masque
        output = Image.new('RGBA', (LOGO_SIZE, LOGO_SIZE), (0, 0, 0, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return output
    except Exception as e:
        print(f"Erreur chargement logo {path}: {e}")
        return None

def draw_multiline_centered(draw, text, font, box, fill):
    # Découpe le texte pour qu'il tienne dans la largeur
    lines = []
    for line in text.split('\n'):
        lines += textwrap.wrap(line, width=22)  # Ajuste width selon la taille de police
    y = box[1]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = box[0] + (box[2] - box[0] - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + 8  # Espacement

def draw_response_text(draw, text, x_start, y_start, max_width, font, fill):
    # Calculer la largeur disponible pour le texte (50% de l'écran - marges)
    available_width = max_width - 40  # 20px de marge de chaque côté
    
    # Découper le texte en lignes
    lines = textwrap.wrap(text, width=20)  # Ajuster width selon la taille de police
    
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = x_start + (available_width - w) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += h + 8

def draw_text_with_glow(draw, text, position, font, text_color, glow_color=(255, 255, 230)):
    # Créer un halo plus large avec des opacités différentes
    for size in range(TEXT_GLOW_SIZE, 0, -1):
        # Opacité plus élevée et plus graduée
        alpha = int(150 * (size / TEXT_GLOW_SIZE))  # Opacité de 150 à 25
        glow = (*glow_color[:3], alpha)
        # Dessiner plusieurs fois pour un effet plus diffus
        for _ in range(2):  # Double le rendu pour plus d'intensité
            for offset in range(-size, size + 1):
                for offset2 in range(-size, size + 1):
                    draw.text((position[0] + offset, position[1] + offset2), text, font=font, fill=glow)
    
    # Dessiner le texte principal
    draw.text(position, text, font=font, fill=text_color)

def calculate_font_size(text_a, text_b, max_width, font_path):
    # Taille de base pour 10 caractères
    base_size = 72
    # Taille minimale de police
    min_size = 40
    
    # Prendre la longueur du texte le plus long
    max_length = max(len(text_a), len(text_b))
    
    # Calculer la taille optimale
    if max_length <= 10:
        return base_size
    
    # Réduire la taille proportionnellement au nombre de caractères
    # Formule : taille = base_size * (10 / max_length)
    # Avec une limite minimale
    size = int(base_size * (10 / max_length))
    return max(size, min_size)

def main():
    # Charger l'image de base
    base = Image.open(BASE_IMAGE_PATH).convert("RGBA").resize((WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)

    # Charger la police
    FONT_PATH = "assets/fonts/Poppins/Poppins-Regular.ttf"
    FONT_BOLD_PATH = "assets/fonts/Poppins/Poppins-Bold.ttf"
    try:
        font_question = ImageFont.truetype(FONT_PATH, size=80)
        # Calculer la taille de police pour les réponses (basée sur le plus long)
        font_size = calculate_font_size(REPONSE_A, REPONSE_B, LOGO_SIZE, FONT_BOLD_PATH)
        font_reponse = ImageFont.truetype(FONT_BOLD_PATH, size=font_size)
    except Exception as e:
        print(f"Erreur chargement police: {e}")
        print(f"Chemins testés : {os.path.abspath(FONT_PATH)} et {os.path.abspath(FONT_BOLD_PATH)}")
        print("Vérifie que les chemins sont corrects et que les fichiers ne sont pas corrompus.")
        return

    # --- Question ---
    question_box = (MARGIN, HEIGHT // 4 - 100, WIDTH - MARGIN, HEIGHT // 4 + 200)
    draw_multiline_centered(draw, QUESTION, font_question, question_box, fill=(255,255,255))

    # --- Logos et textes ---
    y_logos = HEIGHT - int(HEIGHT // 3.2) - LOGO_SIZE // 2
    # Position horizontale pour centrer sur chaque quart
    x_logo_b = 3 * WIDTH // 4 - LOGO_SIZE // 2  # Maintenant à droite
    x_logo_a = WIDTH // 4 - LOGO_SIZE // 2      # Maintenant à gauche

    # Logo B (maintenant à droite)
    logo_b = load_logo(REPONSE_B_IMAGE_PATH)
    if logo_b:
        base.paste(logo_b, (x_logo_b, y_logos), logo_b)
        # Texte sous logo B
        x_text_start = x_logo_b
        y_text = y_logos + LOGO_SIZE + 20
        draw_response_text(draw, REPONSE_B, x_text_start, y_text, LOGO_SIZE, font_reponse, CUVE_B_COLOR_START)

    # Logo A (maintenant à gauche)
    logo_a = load_logo(REPONSE_A_IMAGE_PATH)
    if logo_a:
        base.paste(logo_a, (x_logo_a, y_logos), logo_a)
        # Texte sous logo A
        x_text_start = x_logo_a
        y_text = y_logos + LOGO_SIZE + 20
        draw_response_text(draw, REPONSE_A, x_text_start, y_text, LOGO_SIZE, font_reponse, CUVE_A_COLOR_START)

    # Sauvegarde
    base.save(OUTPUT_PATH)
    print(f"Miniature générée : {OUTPUT_PATH}")

if __name__ == "__main__":
    main()



