import pygame
from core.simulator import Simulator
from config import *

def main():
    # Initialisation
    pygame.init()
    pygame.mixer.init()
    
    # Initialisation de l'affichage
    if VISUAL:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulation de Billes")
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HIDDEN)
    
    # Initialisation et démarrage du simulateur
    simulator = Simulator(WIDTH, HEIGHT)
    simulator.start()
    simulator.run(screen)

if __name__ == "__main__":
    main()
