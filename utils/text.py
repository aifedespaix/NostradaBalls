import pygame
from typing import List

def render_multiline_text(
    text: str,
    font: pygame.font.Font,
    color: tuple,
    max_width: int
) -> List[pygame.Surface]:
    """
    Rend un texte sur plusieurs lignes en respectant une largeur maximale.
    
    Args:
        text (str): Le texte à afficher
        font (pygame.font.Font): La police à utiliser
        color (tuple): La couleur du texte (R, G, B)
        max_width (int): La largeur maximale du texte
        
    Returns:
        List[pygame.Surface]: Liste des surfaces de texte
    """
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_surface = font.render(test_line, True, color)
        if test_surface.get_width() <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Créer les surfaces pour chaque ligne
    surfaces = []
    for line in lines:
        surface = font.render(line, True, color)
        surfaces.append(surface)
    
    return surfaces 