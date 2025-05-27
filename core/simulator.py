import pygame
from typing import Tuple, Optional
from .audio import AudioManager
from .record import RecordManager
from .video_processor import VideoProcessor
from .time import TimeManager
from physics.space import PhysicsSpace
from particles import ParticleManager
from ui.background import Background
from ui.question import Question
from ui.response import Response
from scenes.main import setup_scene
from config import *
import os

class Simulator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Initialisation des gestionnaires
        self.time_manager = TimeManager(fps=FPS, post_physics_duration=DELAI_ARRET)
        self.record_manager = RecordManager(width, height, FPS)
        self.audio_manager = AudioManager()
        self.video_processor = VideoProcessor(self.audio_manager)
        self.physics_space = PhysicsSpace(GRAVITY)
        
        # Initialisation des composants UI
        self.background = Background(width, height)
        self.question = Question(width, height)
        self.response = Response(width, height)
        
        # Initialisation des gestionnaires de jeu
        self.particle_manager = ParticleManager(self.physics_space.get_space())
        self.obstacle_manager, self.cuve_manager = setup_scene(self.physics_space.get_space())
        
        # Variables de jeu
        self.running = True
        self.time_accum = 0
        self.physics_active = True
        self.physics_stop_time = 0
        self.current_gradient = None
        self.gradient_alpha = 0
        self.recording_finished = False

    def start(self):
        """Démarre la simulation et l'enregistrement"""
        self.record_manager.start_recording()
        self.audio_manager.start_recording()
        self.audio_manager.play_sound('background')
        self.audio_manager.play_sound('question')

    def reset(self):
        """Réinitialise la simulation"""
        self.physics_space.reset()
        self.particle_manager = ParticleManager(self.physics_space.get_space())
        self.obstacle_manager, self.cuve_manager = setup_scene(self.physics_space.get_space())
        self.response.set_response(None)
        self.time_manager.reset()
        self.physics_active = True
        self.gradient_alpha = 0
        self.current_gradient = None
        pygame.mixer.music.play(-1)

    def update(self, dt: float) -> bool:
        """Met à jour la simulation. Retourne False si la simulation doit s'arrêter"""
        self.time_accum += dt

        # Mise à jour du TimeManager
        self.time_manager.update_frame()
        if self.physics_active:
            self.time_manager.start_physics()
        else:
            self.time_manager.stop_physics()

        # Mise à jour de l'AudioManager
        self.audio_manager.update_frame(self.time_manager.get_current_state().total_seconds)

        # Émission de particules
        if self.physics_active and self.time_accum >= EMIT_INTERVAL:
            self.particle_manager.emit_particle()
            self.time_accum = 0

        # Mise à jour des obstacles
        self.obstacle_manager.update(dt)

        # Simulation physique
        if self.physics_active:
            for _ in range(20):
                self.physics_space.step(dt / 20)

        # Vérification de la fin de la simulation
        if self.physics_active:
            current_physics_time = self.time_manager.get_current_state().physics_seconds
            if current_physics_time >= TEMPS_LIMITE:
                print(f"Temps limite atteint: {current_physics_time:.1f}s / {TEMPS_LIMITE}s")
                if any(count > 0 and count % SEUIL_VICTOIRE == 0 for count in self.cuve_manager.counts):
                    print(f"Condition de victoire atteinte. Compteurs: {self.cuve_manager.counts}")
                    self.physics_active = False
                    self.physics_stop_time = self.time_manager.get_current_state().total_seconds
                    
                    # Détermination du gagnant
                    if self.cuve_manager.counts[0] > self.cuve_manager.counts[1]:
                        actual_winner = "A"
                        self.response.set_response(REPONSE_B)
                        self.current_gradient = self.background.gradient_surfaces[0]
                        self.audio_manager.play_sound('reponse_b')
                    elif self.cuve_manager.counts[1] > self.cuve_manager.counts[0]:
                        actual_winner = "B"
                        self.response.set_response(REPONSE_A)
                        self.current_gradient = self.background.gradient_surfaces[1]
                        self.audio_manager.play_sound('reponse_a')
                    else:
                        actual_winner = None
                        self.response.set_response("Égalité")
                        self.current_gradient = None

                    # Vérification du gagnant attendu
                    if WINNER == "B" and actual_winner == "A":
                        print("Réinitialisation de la simulation - Mauvais gagnant")
                        self.reset()
                        return True

                    print(f"Simulation arrêtée après {current_physics_time:.1f} secondes")
                    print(f"Nombre de billes dans les cuves: {self.cuve_manager.counts}")

        # Mise à jour de l'alpha du dégradé
        if self.current_gradient and not self.physics_active:
            self.gradient_alpha = min(255, self.gradient_alpha + 8.5)

        # Mise à jour des composants
        self.question.update(dt)
        self.response.update(dt)
        self.cuve_manager.update_counts(self.particle_manager.particles)

        # Vérification de la fin du délai d'arrêt
        if not self.physics_active:
            remaining_time = DELAI_ARRET - (self.time_manager.get_current_state().total_seconds - self.physics_stop_time)
            if remaining_time <= 0 and not self.recording_finished:
                print(f"Délai d'arrêt écoulé: {remaining_time:.1f}s")
                self.recording_finished = True
                return False

        return True

    def draw(self, screen: pygame.Surface) -> bool:
        """Dessine l'état actuel de la simulation"""
        self.background.draw(screen, self.current_gradient, self.gradient_alpha)
        self.obstacle_manager.draw(screen)
        self.cuve_manager.draw(screen)
        self.particle_manager.draw(screen)
        self.question.draw(screen)
        self.response.draw(screen)

        if DEBUG:
            self._draw_debug_info(screen)

        # Enregistrement après le dessin
        if self.record_manager.is_recording():
            if not self.record_manager.record_frame(screen):
                print("Enregistrement terminé")
                self.recording_finished = True
                return False

        return True

    def _draw_debug_info(self, screen: pygame.Surface):
        """Dessine les informations de debug"""
        font = pygame.font.SysFont("Poppins", 24)
        times = self.time_manager.get_formatted_times()
        time_text = font.render(f"Tot: {times['total']} | Phy: {times['physics']} | G: {times['game']} | FPS: {pygame.time.Clock().get_fps():.1f}", True, BLANC)
        screen.blit(time_text, (10, 10))
        
        if not self.physics_active:
            state_text = font.render("Physique arrêtée", True, ROUGE)
            screen.blit(state_text, (10, 40))
            
            remaining_time = DELAI_ARRET - (self.time_manager.get_current_state().total_seconds - self.physics_stop_time)
            if remaining_time > 0:
                countdown_text = font.render(f"Arrêt dans {remaining_time:.1f}s", True, ROUGE)
                screen.blit(countdown_text, (10, 70))

    def stop(self):
        """Arrête proprement la simulation et l'enregistrement"""
        # Arrêter l'enregistrement vidéo
        self.record_manager.stop_recording()
        
        # Arrêter pygame immédiatement
        pygame.mixer.quit()
        pygame.quit()
        print("Application fermée proprement")
        
        # Exporter les événements sonores
        sound_events_path = os.path.join(OUTPUT_DIR, 'sound_events.csv')
        self.audio_manager.export_sound_events(sound_events_path)
        print(f"Événements sonores exportés dans : {sound_events_path}")
        
        try:
            # Générer l'audio
            audio_path = self.video_processor.generate_audio_from_events(sound_events_path)
            if not audio_path:
                raise Exception("Échec de la génération de l'audio")
            print(f"Audio généré avec succès : {audio_path}")
            
            # Vérifier que la vidéo existe
            video_path = self.record_manager.get_video_path()
            if not video_path or not os.path.exists(video_path):
                raise Exception(f"Vidéo non trouvée : {video_path}")
            print(f"Vidéo trouvée : {video_path}")
            
            # Fusionner la vidéo et l'audio
            final_path = self.video_processor.merge_video_audio(
                video_path=video_path,
                audio_path=audio_path,
                fps=FPS
            )
            if not final_path:
                raise Exception("Échec de la fusion vidéo/audio")
            print(f"Fusion terminée avec succès : {final_path}")
            
        except Exception as e:
            print(f"Erreur lors de la génération/fusion audio : {e}")
            import traceback
            traceback.print_exc()

    def run(self, screen: pygame.Surface):
        """Exécute la boucle principale de la simulation"""
        clock = pygame.time.Clock()
        running = True

        while running:
            dt = clock.tick(FPS) / 1000

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            # Mise à jour de la simulation
            if not self.update(dt):
                running = False

            # Dessin
            if not self.draw(screen):
                running = False

            if VISUAL:
                pygame.display.flip()

        # Arrêt propre
        self.stop() 