import os
import imageio_ffmpeg
import subprocess
import pandas as pd
import numpy as np
import soundfile as sf
from scipy import signal
from typing import Optional
from config import TEMPS_LIMITE, DELAI_ARRET, OUTPUT_DIR, THEME

class VideoProcessor:
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.output_dir = OUTPUT_DIR

    def generate_audio_from_events(self, sound_events_path: str, output_audio_path: Optional[str] = None) -> str:
        """
        Génère un fichier audio à partir des événements sonores.
        
        Args:
            sound_events_path (str): Chemin vers le fichier CSV des événements sonores
            output_audio_path (Optional[str]): Chemin de sortie pour le fichier audio
            
        Returns:
            str: Chemin du fichier audio généré
        """
        if output_audio_path is None:
            output_audio_path = os.path.join(self.output_dir, 'audio.wav')
        
        try:
            # Lire les événements sonores
            events_df = pd.read_csv(sound_events_path)
            
            if events_df.empty:
                print("Aucun événement sonore trouvé dans le CSV")
                return None
            
            # Calculer la durée nécessaire en fonction du dernier événement
            sample_rate = 44100  # Taux d'échantillonnage standard
            last_event_time = events_df['Time(s)'].max()
            
            # Trouver le dernier son et sa durée
            last_sound = events_df.iloc[-1]['Sound']
            last_sound_path = self.audio_manager.get_random_sound_variation(last_sound)
            last_sound_duration = 0
            if last_sound_path and os.path.exists(last_sound_path):
                try:
                    last_sound_data, last_sound_rate = sf.read(last_sound_path)
                    # Convertir en mono si nécessaire
                    if len(last_sound_data.shape) > 1:
                        last_sound_data = last_sound_data.mean(axis=1)
                    # Rééchantillonner si nécessaire
                    if last_sound_rate != sample_rate:
                        number_of_samples = round(len(last_sound_data) * sample_rate / last_sound_rate)
                        last_sound_data = signal.resample(last_sound_data, number_of_samples)
                    last_sound_duration = len(last_sound_data) / sample_rate
                    print(f"Durée du dernier son ({last_sound}): {last_sound_duration:.3f}s")
                except Exception as e:
                    print(f"Erreur lors de la lecture du dernier son: {e}")
            
            # Utiliser la durée maximale entre :
            # - Le dernier événement + durée du dernier son + 0.5s de marge
            # - TEMPS_LIMITE + DELAI_ARRET
            duration = max(last_event_time + last_sound_duration + 0.5, TEMPS_LIMITE + DELAI_ARRET)
            print(f"Durée totale calculée: {duration:.3f}s")
            
            # Créer un tableau de silence
            audio_data = np.zeros(int(duration * sample_rate))
            
            # Traiter d'abord la musique de fond
            background_sounds = events_df[events_df['Sound'] == 'background']
            if not background_sounds.empty:
                background_event = background_sounds.iloc[0]
                sound_path = self.audio_manager.get_random_sound_variation('background')
                if sound_path and os.path.exists(sound_path):
                    try:
                        # Lire le fichier audio de la musique de fond
                        bg_sound_data, bg_sample_rate = sf.read(sound_path)
                        
                        # Convertir en mono si stéréo
                        if len(bg_sound_data.shape) > 1:
                            bg_sound_data = bg_sound_data.mean(axis=1)
                        
                        # Rééchantillonner si nécessaire
                        if bg_sample_rate != sample_rate:
                            number_of_samples = round(len(bg_sound_data) * sample_rate / bg_sample_rate)
                            bg_sound_data = signal.resample(bg_sound_data, number_of_samples)
                        
                        # Appliquer le volume de la musique de fond (généralement plus bas)
                        bg_volume = self.audio_manager.get_sound_volume('background')
                        bg_sound_data = bg_sound_data * bg_volume
                        
                        # Répéter la musique de fond pour couvrir toute la durée
                        num_repeats = int(np.ceil(len(audio_data) / len(bg_sound_data)))
                        bg_sound_data = np.tile(bg_sound_data, num_repeats)[:len(audio_data)]
                        
                        # Ajouter la musique de fond
                        audio_data += bg_sound_data
                    except Exception as e:
                        print(f"Erreur lors du traitement de la musique de fond : {e}")
            
            # Traiter les autres sons
            other_sounds = events_df[events_df['Sound'] != 'background']
            print(f"\nTraitement des sons (total: {len(other_sounds)}):")
            for idx, event in other_sounds.iterrows():
                sound_name = event['Sound']
                time = event['Time(s)']
                sample_index = int(time * sample_rate)
                
                sound_path = self.audio_manager.get_random_sound_variation(sound_name)
                if sound_path and os.path.exists(sound_path):
                    try:
                        # Lire le fichier audio
                        sound_data, sound_sample_rate = sf.read(sound_path)
                        
                        # Convertir en mono si stéréo
                        if len(sound_data.shape) > 1:
                            sound_data = sound_data.mean(axis=1)
                        
                        # Rééchantillonner si nécessaire
                        if sound_sample_rate != sample_rate:
                            number_of_samples = round(len(sound_data) * sample_rate / sound_sample_rate)
                            sound_data = signal.resample(sound_data, number_of_samples)
                        
                        # Appliquer le volume
                        volume = self.audio_manager.get_sound_volume(sound_name)
                        sound_data = sound_data * volume
                        
                        # Ajouter le son à la position appropriée
                        if sample_index + len(sound_data) <= len(audio_data):
                            audio_data[sample_index:sample_index + len(sound_data)] += sound_data
                        else:
                            print(f"  - ATTENTION: Le son dépasse la durée totale!")
                            print(f"    - Index de début: {sample_index}")
                            print(f"    - Longueur du son: {len(sound_data)}")
                            print(f"    - Longueur totale: {len(audio_data)}")
                    except Exception as e:
                        print(f"  - ERREUR lors du traitement du son {sound_name}: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"  - Son non trouvé: {sound_name} ({sound_path})")
            
            # Normaliser l'audio avec une limite de crête
            if np.max(np.abs(audio_data)) > 0:
                # Appliquer une compression douce pour éviter la distorsion
                threshold = 0.7
                ratio = 0.8
                mask = np.abs(audio_data) > threshold
                audio_data[mask] = np.sign(audio_data[mask]) * (threshold + (np.abs(audio_data[mask]) - threshold) * ratio)
                # Normaliser final
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Sauvegarder le fichier audio
            print(f"Sauvegarde du fichier audio : {output_audio_path}")
            sf.write(output_audio_path, audio_data, sample_rate)
            print(f"Fichier audio généré : {output_audio_path}")
            
            if not os.path.exists(output_audio_path):
                raise RuntimeError(f"Le fichier audio n'a pas été créé : {output_audio_path}")
            
            return output_audio_path
            
        except Exception as e:
            print(f"Erreur lors de la génération du fichier audio : {e}")
            import traceback
            traceback.print_exc()
            return None

    def merge_video_audio(self, video_path: str, audio_path: str, output_path: Optional[str] = None, fps: int = 60) -> str:
        """
        Fusionne la vidéo et l'audio en utilisant ffmpeg avec des paramètres optimisés pour TikTok.
        
        Args:
            video_path (str): Chemin vers la vidéo
            audio_path (str): Chemin vers l'audio
            output_path (Optional[str]): Chemin de sortie
            fps (int): Images par seconde de la vidéo
            
        Returns:
            str: Chemin du fichier final
        """
        try:
            if not os.path.exists(video_path):
                raise ValueError(f"Fichier vidéo non trouvé : {video_path}")
            
            if not os.path.exists(audio_path):
                raise ValueError(f"Fichier audio non trouvé : {audio_path}")
            
            if output_path is None:
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(os.path.dirname(video_path), f"{video_name}_tiktok-{THEME}.mp4")
            
            print(f"Optimisation pour TikTok : {video_path}")
            print(f"Sortie : {output_path}")
            
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

            # Paramètres optimisés pour TikTok
            command = [
                ffmpeg_path,
                '-hwaccel', 'auto',
                '-i', video_path,
                '-i', audio_path,
                '-map', '0:v',
                '-map', '1:a',
                # Paramètres vidéo optimisés pour TikTok
                '-c:v', 'libx264',
                '-preset', 'slow',  # Meilleure compression
                '-crf', '18',       # Qualité visuelle maximale (0-51, plus bas = meilleure qualité)
                '-profile:v', 'high',
                '-level', '4.2',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                '-r', str(fps),
                # Paramètres audio optimisés
                '-c:a', 'aac',
                '-b:a', '384k',     # Bitrate audio élevé
                '-ar', '48000',     # Taux d'échantillonnage optimal
                '-ac', '2',         # Stéréo
                # Optimisations supplémentaires
                '-threads', '0',     # Utilise tous les threads disponibles
                '-y',
                output_path
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print("Erreur lors de l'optimisation :")
                print(stderr)
                raise RuntimeError("Échec de l'optimisation pour TikTok")
            
            if not os.path.exists(output_path):
                raise RuntimeError(f"Le fichier optimisé n'a pas été créé : {output_path}")
            
            print(f"Optimisation TikTok terminée avec succès : {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Erreur lors de l'optimisation pour TikTok : {e}")
            import traceback
            traceback.print_exc()
            return None 