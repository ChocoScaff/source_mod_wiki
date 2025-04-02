#!/usr/bin/env python3
"""
Script pour convertir une série de fichiers Markdown en PDF et EPUB.
Optimisé pour utiliser moins de mémoire en divisant le travail en lots.
"""

import os
import argparse
import subprocess
import glob
import re
import datetime
import shutil
import tempfile
import time
from math import ceil


def natural_sort_key(s):
    """Fonction pour trier les fichiers de manière naturelle (chapitre1, chapitre2, ..., chapitre10)"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]


def find_image_references(markdown_files):
    """
    Trouve toutes les références d'images dans les fichiers markdown.
    """
    image_paths = set()
    image_pattern = re.compile(r'!\[.*?\]\((.*?)(?:\s+["\'](.*?)["\']\s*)?\)')
    
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for match in image_pattern.finditer(content):
                    image_path = match.group(1)
                    if image_path:
                        image_paths.add(image_path)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
    
    return image_paths


def copy_images_to_temp_dir(image_references, base_dir, temp_dir):
    """
    Copie les images référencées vers un répertoire temporaire.
    """
    path_mapping = {}
    img_dir = os.path.join(temp_dir, "img")
    os.makedirs(img_dir, exist_ok=True)
    
    for img_path in image_references:
        absolute_img_path = img_path
        if not os.path.isabs(img_path):
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
            new_img_path = os.path.join(img_dir, os.path.basename(img_path))
            shutil.copy2(absolute_img_path, new_img_path)
            path_mapping[img_path] = os.path.join("img", os.path.basename(img_path))
            print(f"Image copiée: {img_path} -> {os.path.join('img', os.path.basename(img_path))}")
        else:
            print(f"Avertissement: Image non trouvée - {img_path}")
    
    return path_mapping


def update_image_references(content, path_mapping):
    """
    Met à jour les références d'images dans le contenu markdown.
    """
    image_pattern = re.compile(r'(!\[.*?\]\()(.+?)(\s+["\'](.*?)["\']\s*)?(\))')
    
    def replace_match(match):
        prefix = match.group(1)
        img_path = match.group(2)
        middle = match.group(3) or ""
        suffix = match.group(5)
        
        if img_path in path_mapping:
            return f"{prefix}{path_mapping[img_path]}{middle}{suffix}"
        return match.group(0)
    
    return image_pattern.sub(replace_match, content)


def create_batch_pdf(batch_files, temp_dir, output_pdf, metadata_path):
    """
    Crée un PDF à partir d'un lot de fichiers markdown.
    """
    print(f"Création d'un PDF avec {len(batch_files)} fichiers...")
    
    cmd = [
        "pandoc",
        "-f", "markdown",
        "-o", output_pdf,
        "--resource-path", temp_dir,
        metadata_path,
    ] + batch_files
    
    try:
        subprocess.run(cmd, check=True, cwd=temp_dir, timeout=300)  # 5 minutes timeout
        return True
    except subprocess.SubprocessError as e:
        print(f"Erreur lors de la création du PDF: {e}")
        return False


def merge_pdfs(pdf_files, output_pdf):
    """
    Fusionne plusieurs fichiers PDF en un seul.
    Utilise PyPDF2 si disponible, sinon essaie avec pdftk, puis avec gs.
    """
    try:
        from PyPDF2 import PdfMerger
        merger = PdfMerger()
        for pdf in pdf_files:
            if os.path.exists(pdf):
                merger.append(pdf)
        merger.write(output_pdf)
        merger.close()
        print(f"PDF fusionnés avec PyPDF2: {output_pdf}")
        return True
    except ImportError:
        print("PyPDF2 non disponible, tentative avec pdftk...")
        
        # Essayer avec pdftk
        try:
            cmd = ["pdftk"] + pdf_files + ["cat", "output", output_pdf]
            subprocess.run(cmd, check=True)
            print(f"PDF fusionnés avec pdftk: {output_pdf}")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("pdftk non disponible, tentative avec ghostscript...")
            
            # Essayer avec ghostscript
            try:
                cmd = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", f"-sOutputFile={output_pdf}"] + pdf_files
                subprocess.run(cmd, check=True)
                print(f"PDF fusionnés avec ghostscript: {output_pdf}")
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Aucun outil de fusion PDF disponible. Installation de PyPDF2 recommandée: pip install PyPDF2")
                return False


def create_book_in_batches(input_dir, output_name, title, author, batch_size=3, create_pdf=True, create_epub=True):
    """
    Convertit des fichiers markdown en PDF et/ou EPUB en divisant le travail en lots.
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
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Mettre à jour les références d'images
                updated_content = update_image_references(content, path_mapping)
                
                # Écrire le contenu mis à jour dans un fichier temporaire
                temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                temp_markdown_files.append(temp_file_path)
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {file_path}: {e}")

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

        # Créer l'EPUB (un seul fichier, généralement moins intensif en mémoire)
        if create_epub:
            output_epub = f"{output_name}.epub"
            print(f"\nCréation de l'EPUB: {output_epub}...")
            
            cmd = [
                "pandoc",
                "-f", "markdown",
                "-t", "epub",
                "-o", os.path.abspath(output_epub),
                "--resource-path", temp_dir,
                "--toc",
                "--toc-depth=2",
                metadata_path,
            ] + temp_markdown_files
            
            try:
                subprocess.run(cmd, check=True, cwd=temp_dir, timeout=600)  # 10 minutes timeout
                print(f"EPUB créé avec succès: {output_epub}")
            except subprocess.SubprocessError as e:
                print(f"Erreur lors de la création de l'EPUB: {e}")

        # Créer le PDF en lots
        if create_pdf:
            final_pdf = f"{output_name}.pdf"
            print(f"\nCréation du PDF par lots: {final_pdf}...")
            
            # Diviser les fichiers en lots
            num_batches = ceil(len(temp_markdown_files) / batch_size)
            pdf_parts = []
            
            for i in range(num_batches):
                start_idx = i * batch_size
                end_idx = min(start_idx + batch_size, len(temp_markdown_files))
                batch = temp_markdown_files[start_idx:end_idx]
                
                # Nom du fichier PDF pour ce lot
                batch_pdf = os.path.join(temp_dir, f"part_{i+1}.pdf")
                pdf_parts.append(batch_pdf)
                
                # Créer le PDF pour ce lot
                success = create_batch_pdf(batch, temp_dir, batch_pdf, metadata_path)
                
                if not success:
                    print(f"Échec de la création du lot {i+1}/{num_batches}. Tentative avec un lot plus petit...")
                    
                    # Essayer avec un lot encore plus petit si nécessaire
                    for j, file in enumerate(batch):
                        single_batch_pdf = os.path.join(temp_dir, f"part_{i+1}_{j+1}.pdf")
                        if create_batch_pdf([file], temp_dir, single_batch_pdf, metadata_path):
                            if os.path.exists(single_batch_pdf):
                                pdf_parts.append(single_batch_pdf)
                                if batch_pdf in pdf_parts:
                                    pdf_parts.remove(batch_pdf)
                        time.sleep(1)  # Petite pause entre les conversions
                
                # Petite pause entre les lots pour libérer la mémoire
                time.sleep(2)
            
            # Fusionner les PDFs
            pdf_parts = [p for p in pdf_parts if os.path.exists(p)]
            if pdf_parts:
                print(f"Fusion de {len(pdf_parts)} fichiers PDF...")
                if merge_pdfs(pdf_parts, final_pdf):
                    print(f"PDF créé avec succès: {final_pdf}")
                else:
                    print(f"Échec de la fusion des PDF. Les parties sont disponibles dans: {', '.join(pdf_parts)}")
                    # Copier les parties dans le répertoire de travail si la fusion échoue
                    for i, part in enumerate(pdf_parts):
                        shutil.copy(part, f"{output_name}_part_{i+1}.pdf")
                    print("Les fichiers PDF partiels ont été copiés dans le répertoire de travail.")
            else:
                print("Aucune partie PDF créée. Conversion échouée.")


def main():
    parser = argparse.ArgumentParser(description="Convertir des fichiers markdown en PDF et EPUB")
    parser.add_argument("input_dir", help="Répertoire contenant les fichiers markdown")
    parser.add_argument("--output", "-o", default="livre", help="Nom du fichier de sortie (sans extension)")
    parser.add_argument("--title", "-t", default="Mon Livre", help="Titre du livre")
    parser.add_argument("--author", "-a", default="Auteur", help="Auteur du livre")
    parser.add_argument("--batch-size", "-b", type=int, default=3, help="Nombre de fichiers par lot (défaut: 3)")
    parser.add_argument("--pdf-only", action="store_true", help="Créer uniquement le PDF")
    parser.add_argument("--epub-only", action="store_true", help="Créer uniquement l'EPUB")
    
    args = parser.parse_args()
    
    create_pdf = not args.epub_only
    create_epub = not args.pdf_only
    
    create_book_in_batches(
        args.input_dir, 
        args.output, 
        args.title, 
        args.author,
        batch_size=args.batch_size,
        create_pdf=create_pdf, 
        create_epub=create_epub
    )


if __name__ == "__main__":
    main()