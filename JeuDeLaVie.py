
import tkinter as tk
import numpy   as np
from mpi4py import MPI
from math import log

class grille:
    """
    Grille torique décrivant l'automate cellulaire.
    En entrée lors de la création de la grille :
        - dimensions est un tuple contenant le nombre de cellules dans les deux directions (nombre lignes, nombre colonnes)
        - init_pattern est une liste de cellules initialement vivantes sur cette grille (les autres sont considérées comme mortes)
        - color_life est la couleur dans laquelle on affiche une cellule vivante
        - color_dead est la couleur dans laquelle on affiche une cellule morte
    Si aucun pattern n'est donné, on tire au hasard quels sont les cellules vivantes et les cellules mortes
    Exemple :
       grid = grille( (10,10), init_pattern=[(2,2),(0,2),(4,2),(2,0),(2,4)], color_life="red", color_dead="black")
    """
    def __init__( self, dim, init_pattern = None,gridcells=None,n=0,nbeg=0,color_life = ["black","red"], color_dead = "white" ):
        import random
        self.dimensions = dim
        if init_pattern is not None and gridcells is None:
            self.cells = np.zeros(self.dimensions, dtype=np.uint8)  
            indices_i = [v[0] for v in init_pattern]
            indices_j = [v[1] for v in init_pattern]
            self.cells[indices_i,indices_j] = [v[2] for v in init_pattern]
        elif gridcells is not None:
            self.cells=gridcells
        else:
            self.cells = np.random.randint(3, size=dim, dtype=np.uint8)
        self.col_life = color_life        
        self.col_dead = color_dead
        self.nbeg=nbeg
        self.n=n

    def compute_next_iteration(self):
        """
        Calcule la prochaine génération de cellules en suivant les règles du jeu de la vie
        """
        # Remarque 1: on pourrait optimiser en faisant du vectoriel, mais pour plus de clarté, on utilise les boucles
        # Remarque 2: on voit la grille plus comme une matrice qu'une grille géométrique. L'indice (0,0) est donc en haut
        #             à gauche de la grille !
        
        ny = self.dimensions[0]
        nx = self.dimensions[1]
        next_cells = np.zeros(self.dimensions, dtype=np.uint8) #=self.cells[:,nbeg:nend+1]
        diff_cells = []
        
        if rank==0:
            self.cells[:,0]=com.recv(source=size-1)
            com.send(self.cells[:,1],dest=size-1)
            self.cells[:,-1]=com.recv(source=1)
            com.send(self.cells[:,-2],dest=1)
        elif rank==size-1:
            self.cells[:,0]=com.recv(source=size-2)
            com.send(self.cells[:,1],dest=size-2)
            com.send(self.cells[:,-2],dest=0)
            self.cells[:,-1]=com.recv(source=0)
        else:
            com.send(self.cells[:,-2],dest=rank+1)
            self.cells[:,-1]=com.recv(source=rank+1)
            com.send(self.cells[:,1],dest=rank-1)
            self.cells[:,0]=com.recv(source=rank-1)
        
        for i in range(0,ny):
            i_above = (i+ny-1)%ny
            i_below = (i+1)%ny
            for j in range(1,nx-1):
                j_left = (j-1+nx)%nx
                j_right= (j+1)%nx
                voisins_i = [i_above,i_above,i_above, i     , i      , i_below, i_below, i_below]
                voisins_j = [j_left ,j      ,j_right, j_left, j_right, j_left , j      , j_right]
                voisines = np.array(self.cells[voisins_i,voisins_j])
                nb_voisines_vivantes = np.sum(voisines!=0)
                nb_voisines1         = np.sum(voisines==1)
                nb_voisines2         = np.sum(voisines==2)
                #print(f"voisins : {nb_voisines_vivantes}, voisins1 : {nb_voisines1}, voisins2 : {nb_voisines2}")
                if self.cells[i,j] != 0: # Si la cellule est vivante
                    if (nb_voisines_vivantes < 2) or (nb_voisines_vivantes > 3):
                        next_cells[i,j] = 0 # Cas de sous ou sur population, la cellule meurt
                        #if(j!=0 and j!=nx-1):
                        diff_cells.append(i*(self.n)+j+self.nbeg-1)
                    else:
                        next_cells[i,j] = self.cells[i,j] # Sinon elle reste vivante
                elif nb_voisines_vivantes == 3: # Cas où cellule morte mais entourée exactement de trois vivantes
                    if (nb_voisines1 > nb_voisines2):
                        next_cells[i,j] = 1         # Naissance de la cellule
                    else:
                        next_cells[i,j] = 2
                    #if(j!=0 and j!=nx-1):
                    diff_cells.append(i*(self.n)+j+self.nbeg-1)
                else:
                    next_cells[i,j] = 0 # Morte, elle reste morte.
        #if rank==1:
         #   print(next_cells[:,1:nx-1])
        #cells2 = com.allgather(next_cells[:,1:nx-1])
        #cells2=np.reshape(cells2,(self.dimensions[0],self.dimensions[1]))
        #diff_cells2 = com.allgather(diff_cells)
        #diff_cells2=[j for L in diff_cells2 for j in L]
        self.cells = next_cells
        return diff_cells
    
    
class App:
    """
    Cette classe décrit la fenêtre affichant la grille à l'écran
        - geometry est un tuple de deux entiers donnant le nombre de pixels verticaux et horizontaux (dans cet ordre)
        - grid est la grille décrivant l'automate cellulaire (voir plus haut)
    """
    def __init__(self, geometry, grid):
        self.grid = grid
        # Calcul de la taille d'une cellule par rapport à la taille de la fenêtre et de la grille à afficher :
        self.size_x = geometry[1]//grid.dimensions[1]
        self.size_y = geometry[0]//grid.dimensions[0]
        if self.size_x > 4 and self.size_y > 4 :
            self.draw_color='black'
        else:
            self.draw_color=""
        # Ajustement de la taille de la fenêtre pour bien fitter la dimension de la grille
        self.width = grid.dimensions[1] * self.size_x
        self.height= grid.dimensions[0] * self.size_y
        # Création de la fenêtre à l'aide de tkinter
        self.root = tk.Tk()
        # Création de l'objet d'affichage
        self.canvas = tk.Canvas(self.root, height = self.height, width = self.width)
        self.canvas.pack()
        #
        self.canvas_cells = []

    def compute_rectangle(self, i : int, j : int):
        """
        Calcul la géométrie du rectangle correspondant à la cellule (i,j)
        """
        return (self.size_x*j,self.height - self.size_y*i - 1, self.size_x*j+self.size_x-1, self.height - self.size_y*(i+1) )

    def compute_color(self,i : int,j : int):
        if self.grid.cells[i,j] == 0:
            return self.grid.col_dead
        elif self.grid.cells[i,j] == 1:
            return self.grid.col_life[0]
        else:
            return self.grid.col_life[1]
            
    def draw(self, diff):
        if len(self.canvas_cells) == 0:
            # Création la première fois des cellules en tant qu'entité graphique :
            self.canvas_cells = [self.canvas.create_rectangle(*self.compute_rectangle(i,j), fill=self.compute_color(i,j),outline=self.draw_color) for i in range(self.grid.dimensions[0]) for j in range(self.grid.dimensions[1])]
        else:
            nx = self.grid.dimensions[1]
            [self.canvas.itemconfig(self.canvas_cells[ind], fill=self.compute_color(ind//nx,ind%nx),outline=self.draw_color) for ind in diff]
        self.root.update_idletasks()
        self.root.update()

# python lifegame toad
# python lifegame beacon
if __name__ == '__main__':
    import time
    import sys
    dico_patterns = { # Dimension et pattern dans un tuple
        'blinker' : ((5,5),[(2,1,1),(2,2,2),(2,3,2)]),
        'toad'    : ((6,6),[(2,2,1),(2,3,1),(2,4,1),(3,3,2),(3,4,2),(3,5,2)]),
        "acorn"   : ((100,100), [(51,52,1),(52,54,2),(53,51,1),(53,52,1),(53,55,2),(53,56,2),(53,57,2)]),
        "beacon"  : ((6,6), [(1,3,1),(1,4,1),(2,3,1),(2,4,1),(3,1,2),(3,2,2),(4,1,2),(4,2,2)]),
        "boat" : ((5,5),[(1,1,1),(1,2,1),(2,1,2),(2,3,2),(3,2,2)]),
        "glider": ((100,90),[(1,1,1),(2,2,2),(2,3,2),(3,1,1),(3,2,1)]),
        "glider_gun": ((200,100),[(51,76,1),(52,74,1),(52,76,1),(53,64,1),(53,65,1),(53,72,2),(53,73,2),(53,86,2),(53,87,2),(54,63,2),(54,67,2),(54,72,1),(54,73,1),(54,86,1),(54,87,1),(55,52,1),(55,53,1),(55,62,1),(55,68,1),(55,72,1),(55,73,1),(56,52,2),(56,53,2),(56,62,2),(56,66,2),(56,68,2),(56,69,2),(56,74,2),(56,76,2),(57,62,2),(57,68,2),(57,76,2),(58,63,2),(58,67,2),(59,64,2),(59,65,2)]),
        "space_ship": ((25,25),[(11,13,1),(11,14,1),(12,11,1),(12,12,1),(12,14,1),(12,15,1),(13,11,2),(13,12,2),(13,13,2),(13,14,2),(14,12,2),(14,13,2)]),
        "die_hard" : ((100,100), [(51,57,1),(52,51,1),(52,52,1),(53,52,2),(53,56,2),(53,57,2),(53,58,2)]),
        "pulsar": ((17,17),[(2,4,1),(2,5,1),(2,6,1),(7,4,1),(7,5,1),(7,6,1),(9,4,1),(9,5,1),(9,6,1),(14,4,1),(14,5,1),(14,6,1),(2,10,2),(2,11,2),(2,12,2),(7,10,2),(7,11,2),(7,12,2),(9,10,2),(9,11,2),(9,12,2),(14,10,2),(14,11,2),(14,12,2),(4,2,1),(5,2,2),(6,2,1),(4,7,2),(5,7,1),(6,7,2),(4,9,1),(5,9,2),(6,9,1),(4,14,2),(5,14,1),(6,14,2),(10,2,1),(11,2,2),(12,2,1),(10,7,2),(11,7,1),(12,7,2),(10,9,1),(11,9,2),(12,9,1),(10,14,2),(11,14,1),(12,14,2)])
    }
    
    choice = 'acorn'
    init_pattern = dico_patterns[choice]
    grid = grille(*init_pattern)
    
  
    com=MPI.COMM_WORLD.Dup()
    size=com.size
    rank=com.rank
        
    rang_voisinage = 2
    nbeg=rank*(grid.dimensions[1]//size)
    nend=(rank+1)*(grid.dimensions[1]//size)-1+(grid.dimensions[1]%size)*(rank==size-1)
    
    ny = grid.dimensions[0]
    nx = len(np.arange(nbeg,nend+1))
    
    def newGenation(grid):
        
        cell = np.column_stack((np.zeros(grid.dimensions[0]),grid.cells[:,nbeg:nend+1],np.zeros(grid.dimensions[0])) )
    
        gridloc=grille(dim=(ny,nx+2),gridcells=cell,n=grid.dimensions[1],nbeg=nbeg)
    
        diffloc=gridloc.compute_next_iteration()
        
        diff_final=com.allgather(diffloc)
    
        diff_final=[i for L in diff_final for i in L]
        
        finalgrid= com.allgather(gridloc.cells[:,1:nx+1])
        result= np.hstack(finalgrid)
        
        grid.cells=result
        
        return diff_final
     

    if len(sys.argv) > 1 :
        choice = sys.argv[1]
    resx = 800
    resy = 800
    if len(sys.argv) > 3 :
        resx = int(sys.argv[2])
        resy = int(sys.argv[3])
    if rank==0:
        print(f"Pattern initial choisi : {choice}",flush=True)
        print(f"resolution ecran : {resx,resy}")
    
    appli = App((resx,resy),grid)
    if grid.dimensions[1]>=size:
        while(True):
            t1=time.time()
            diff=newGenation(grid)
            t2=time.time()
            if(rank==0):
                appli.draw(diff)
            
            t3=time.time()
            
            print(f"Temps calcul prochaine generation : {t2-t1:2.2e} secondes, temps affichage : {t3-t2:2.2e} secondes\n", end='')
    
    else:
        print("ERROR: Nombre de colonnes inférieur aux nombres de processus")

