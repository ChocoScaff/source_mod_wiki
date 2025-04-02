#!/usr/bin/env python3
"""
Script pour convertir une série de fichiers Markdown en PDF et EPUB.
Utilise Pandoc pour la conversion et gère correctement les chemins d'images.
"""

import os
import argparse
import subprocess
import glob
import re
import datetime
import shutil
import tempfile


def natural_sort_key(s):
    """Fonction pour trier les fichiers de manière naturelle (chapitre1, chapitre2, ..., chapitre10)"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


def find_image_references(markdown_files):
    """
    Trouve toutes les références d'images dans les fichiers markdown.
    
    Args:
        markdown_files: Liste des chemins vers les fichiers markdown
        
    Returns:
        Un ensemble de chemins d'images référencées
    """
    image_paths = set()
    # Regex pour trouver les références d'images en Markdown
    image_pattern = re.compile(r'!\[.*?\]\((.*?)(?:\s+["\'](.*?)["\']\s*)?\)')
    
    for file_path in markdown_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for match in image_pattern.finditer(content):
                image_path = match.group(1)
                if image_path:
                    image_paths.add(image_path)
    
    return image_paths


def copy_images_to_temp_dir(image_references, base_dir, temp_dir):
    """
    Copie les images référencées vers un répertoire temporaire et retourne un dictionnaire
    de correspondance entre ancien et nouveau chemin.
    
    Args:
        image_references: Ensemble des chemins d'images référencées
        base_dir: Répertoire de base pour résoudre les chemins relatifs
        temp_dir: Répertoire temporaire où copier les images
        
    Returns:
        Un dictionnaire {ancien_chemin: nouveau_chemin}
    """
    path_mapping = {}
    img_dir = os.path.join(temp_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    for img_path in image_references:
        # Essayer de résoudre le chemin absolu de l'image
        absolute_img_path = img_path
        if not os.path.isabs(img_path):
            # Essayer différentes possibilités pour trouver l'image
            possible_paths = [
                os.path.join(base_dir, img_path),
                os.path.join(base_dir, 'img', os.path.basename(img_path)),
                os.path.join(base_dir, '..', 'img', os.path.basename(img_path))
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    absolute_img_path = path
                    break
        
        if os.path.exists(absolute_img_path):
            # Déterminer le nouveau chemin dans le répertoire temporaire
            new_img_path = os.path.join(img_dir, os.path.basename(img_path))
            
            # Copier l'image
            shutil.copy2(absolute_img_path, new_img_path)
            
            # Ajouter au dictionnaire de correspondance
            path_mapping[img_path] = os.path.join("img", os.path.basename(img_path))
            print(f"Image copiée: {img_path} -> {os.path.join('img', os.path.basename(img_path))}")
        else:
            print(f"Avertissement: Image non trouvée - {img_path}")
    
    return path_mapping


def update_image_references(content, path_mapping):
    """
    Met à jour les références d'images dans le contenu markdown.
    
    Args:
        content: Contenu markdown
        path_mapping: Dictionnaire {ancien_chemin: nouveau_chemin}
        
    Returns:
        Contenu markdown mis à jour
    """
    # Regex pour trouver les références d'images en Markdown
    image_pattern = re.compile(r'(!\[.*?\]\()(.+?)(\s+["\'](.*?)["\']\s*)?(\))')
    
    def replace_match(match):
        prefix = match.group(1)  # ![alt](
        img_path = match.group(2)  # path/to/image.png
        middle = match.group(3) or ""  # Optional title part
        suffix = match.group(5)  # )
        
        if img_path in path_mapping:
            return f"{prefix}{path_mapping[img_path]}{middle}{suffix}"
        return match.group(0)
    
    return image_pattern.sub(replace_match, content)


def create_book(input_dir, output_name, title, author, create_pdf=True, create_epub=True):
    """
    Convertit des fichiers markdown en PDF et/ou EPUB en gérant correctement les images.
    
    Args:
        input_dir: Répertoire contenant les fichiers markdown
        output_name: Nom du fichier de sortie (sans extension)
        title: Titre du livre
        author: Auteur du livre
        create_pdf: Booléen indiquant si on doit créer un PDF
        create_epub: Booléen indiquant si on doit créer un EPUB
    """
    # Vérifier que Pandoc est installé
    try:
        subprocess.run(["pandoc", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Erreur: Pandoc n'est pas installé. Veuillez l'installer: https://pandoc.org/installing.html")
        return

    # Trouver tous les fichiers markdown dans le répertoire
    markdown_files = []
    for ext in ["*.md", "*.markdown"]:
        markdown_files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    # Trier les fichiers par ordre naturel
    markdown_files.sort(key=natural_sort_key)
    
    if not markdown_files:
        print(f"Aucun fichier markdown trouvé dans {input_dir}")
        return

    print(f"Fichiers trouvés: {len(markdown_files)}")
    for file in markdown_files:
        print(f"  - {os.path.basename(file)}")

    # Créer un répertoire temporaire pour travailler avec les fichiers
    with tempfile.TemporaryDirectory() as temp_dir:
        # Trouver toutes les références d'images
        image_references = find_image_references(markdown_files)
        print(f"Références d'images trouvées: {len(image_references)}")
        
        # Copier les images vers le répertoire temporaire
        path_mapping = copy_images_to_temp_dir(image_references, input_dir, temp_dir)
        
        # Créer des copies temporaires des fichiers markdown avec les références d'images mises à jour
        temp_markdown_files = []
        for file_path in markdown_files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Mettre à jour les références d'images
            updated_content = update_image_references(content, path_mapping)
            
            # Écrire le contenu mis à jour dans un fichier temporaire
            temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            temp_markdown_files.append(temp_file_path)

        # Créer un fichier metadata.yaml pour les métadonnées
        metadata_path = os.path.join(temp_dir, "metadata.yaml")
        with open(metadata_path, "w", encoding="utf-8") as f:
            current_date = datetime.date.today().strftime('%Y-%m-%d')
            f.write(f"""---
title: "{title}"
author: "{author}"
lang: fr-FR
date: "{current_date}"
documentclass: book
geometry: "margin=1in"
toc: true
toc-depth: 2
---
""")

        # Créer le PDF
        if create_pdf:
            output_pdf = f"{output_name}.pdf"
            print(f"\nCréation du PDF: {output_pdf}...")
            
            cmd = [
                "pandoc",
                "-f", "markdown",
                "-o", os.path.abspath(output_pdf),  # Utiliser un chemin absolu
                "--resource-path", temp_dir,  # Définir le chemin de recherche des ressources
                metadata_path,
            ] + temp_markdown_files
            
            try:
                subprocess.run(cmd, check=True, cwd=temp_dir)  # Exécuter dans le répertoire temporaire
                print(f"PDF créé avec succès: {output_pdf}")
            except subprocess.SubprocessError as e:
                print(f"Erreur lors de la création du PDF: {e}")

        # Créer l'EPUB
        if create_epub:
            output_epub = f"{output_name}.epub"
            print(f"\nCréation de l'EPUB: {output_epub}...")
            
            cmd = [
                "pandoc",
                "-f", "markdown",
                "-t", "epub",
                "-o", os.path.abspath(output_epub),  # Utiliser un chemin absolu
                "--resource-path", temp_dir,  # Définir le chemin de recherche des ressources
                "--toc",
                "--toc-depth=2",
                metadata_path,
            ] + temp_markdown_files
            
            try:
                subprocess.run(cmd, check=True, cwd=temp_dir)  # Exécuter dans le répertoire temporaire
                print(f"EPUB créé avec succès: {output_epub}")
            except subprocess.SubprocessError as e:
                print(f"Erreur lors de la création de l'EPUB: {e}")


def main():
    parser = argparse.ArgumentParser(description="Convertir des fichiers markdown en PDF et EPUB")
    parser.add_argument("input_dir", help="Répertoire contenant les fichiers markdown")
    parser.add_argument("--output", "-o", default="livre", help="Nom du fichier de sortie (sans extension)")
    parser.add_argument("--title", "-t", default="Mon Livre", help="Titre du livre")
    parser.add_argument("--author", "-a", default="Auteur", help="Auteur du livre")
    parser.add_argument("--pdf-only", action="store_true", help="Créer uniquement le PDF")
    parser.add_argument("--epub-only", action="store_true", help="Créer uniquement l'EPUB")
    
    args = parser.parse_args()
    
    create_pdf = not args.epub_only
    create_epub = not args.pdf_only
    
    create_book(
        args.input_dir, 
        args.output, 
        args.title, 
        args.author, 
        create_pdf=create_pdf, 
        create_epub=create_epub
    )


if __name__ == "__main__":
    main()