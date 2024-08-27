# Système de dialogue

Ce chapitre a pour but de vous créer des dialogues avec vos npc. Nous allons utiliser le logiciel *hlfaceposer*.*exe* dans le dossier bin du moteur source.

## Expression

Le système *Flex Sliders* pemet de tester les expressions de votre personnage

![](img/image87.png)

Pour sauvegarder les expressions, il faut créer un fichier *.txt* dans le dossier expressions (cf. [Exemple expressions.txt](ressource/expressions.txt) )

![](img/image88.png)

Ce fichier contient les variables des *flex sliders*.

![](img/image89.png)


Vous pouvez voire tous les expressions lister dans le fichier avec la fenêtre expression.

![](img/image90.png)

## Choreography

Crée un nouveau fichier *.vcd* dans le dossier *scene* avec *Choreography->new...*

Nommer votre acteur

![](img/image91.png)

Cliquer sur le nom de votre acteur et crée un nouveau *channel* associer à un acteur. Les *channel* sont comme une timeline dans les logiciels de montage.

![](img/image92.png)

Vous pouvez mettre votre fichier audio, les expressions et les gestures de la scène.

![](img/image93.png)

## Dialogue dans Hammer

Placer un *logic_choreographed_scene* dans *hammer* et sélectionner votre fichier *.vcd*

![](img/image94.png)

<div style="page-break-after: always"></div>