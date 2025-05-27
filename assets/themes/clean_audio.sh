#!/bin/bash

echo "🔍 Recherche des fichiers .wav > 50 Mo..."

find . -type f -name "*.wav" -size +50M | while read -r original; do
    echo "🎧 Compression de : $original"

    # Nom temporaire pour fichier compressé
    temp="${original%.wav}_temp.wav"

    # Compression avec ffmpeg
    ffmpeg -y -i "$original" -c:a adpcm_ima_wav "$temp"

    # Vérifie si la compression a réussi
    if [ -f "$temp" ]; then
        original_size=$(du -m "$original" | cut -f1)
        compressed_size=$(du -m "$temp" | cut -f1)

        # Remplace l'ancien fichier seulement si le nouveau est plus petit
        if [ "$compressed_size" -lt "$original_size" ]; then
            mv "$temp" "$original"
            echo "✅ Compressé : $original_size Mo → $compressed_size Mo"
        else
            echo "⚠️ Compression inutile (taille identique ou plus grande), on garde l'original."
            rm "$temp"
        fi
    else
        echo "❌ Erreur lors de la compression de : $original"
    fi
done

echo "✅ Fini."
