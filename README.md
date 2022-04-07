# Calcul-parall-le

Automate cellulaire
###################

Un automate cellulaire est une machine à état se basant sur des règles normalement simples. Ici, on va
s'intéresser à un automate cellulaire sur une grille à deux dimensions où chaque cellule possède deux
caractéristiques :
    - Un état mort ou vivant
    - Si vivant, une couleur définie parmi deux couleurs

A l'initiation, on impose certaines cellules vivantes avec une certaine couleur et les autres mortes.

Le principe est alors d'itérer de telle sorte qu'à chaque itération, une cellule va devoir interagir avec 
ses huit cellules voisines (gauche, droite, haut, bas et les diagonales). L'interaction se fait selon les 
règles suivantes pour calculer l'interaction suivante :
    - Une cellule vivante avec moins de deux cellules voisines vivantes meurt (sous-population)
    - Une cellule vivante avec deux ou trois cellules voisines vivantes reste vivante 
    - Une cellule vivante avec plus de trois cellules voisines vivantes meurt (sur-population)
    - Une cellule morte avec exactement trois cellules voisines vivantes devient vivante et prend la couleur majoritaire des cellules voisines vivantes

Pour ce projet, on choisit une grille infinie définie par un tore contenant un
nombre fini de cellules. Les cellules les plus à gauche ont pour voisines les cellules les plus à droite
et inversement, et de même les cellules les plus en haut ont pour voisines les cellules les plus en bas
et inversement.
