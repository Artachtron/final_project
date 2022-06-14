
#%% 
import numpy as np
import pygame as pg
import os, sys
#sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')))
from grid import Grid
from entities import Animal
import entities
import world
from itertools import combinations

# %%
pos = (5,5)
value = Animal
grid = Grid(height=20, width=20)
world.init_pygame()
grid.create_entity("animal" ,position=(5,6))
grid.create_entity("animal" ,position=(5,4))
grid.create_entity("tree" ,position=(6,5))
pg.quit()
subgrid = grid.entity_grid
# %%
def python(radius: int=1):
    cells =  set()
    for x in range(-radius,radius+1):
        for y in range(-radius,radius+1):
            coordinate = tuple(np.add(pos,(x,y)))
            if issubclass(type(subgrid.get_cell_value(cell_coordinates=coordinate)),value):
                cells.add(coordinate)
    return cells

def numpy():
    r = np.arange(-1,2)
    s = np.stack(np.meshgrid(r,r)).T.reshape(-1, 2) + pos
    
    return s[[issubclass(type(subgrid.subgrid[tuple(c)]),value) for c in s]]
  
def numpy2():
    r = np.arange(-1,2)
    s = np.stack(np.meshgrid(r,r)).T.reshape(-1, 2) + pos
        
    return s[[issubclass(type(subgrid.get_cell_value(cell_coordinates=c)),value) for c in s]]  

def mixed(radius: int=1):
    cells =  set()
    for x in range(-radius,radius+1):
        for y in range(-radius,radius+1):
            coordinate = tuple(np.add(pos,(x,y)))
            cells.add(coordinate)
            
    s = np.array(list(cells))
    return s[[issubclass(type(subgrid.get_cell_value(cell_coordinates=c)),value) for c in s]]

def permutation():
    a = [-1,0,1]
    b = combinations(a*2, 2)
    #positions = [tuple(np.add(pos,(x,y))) for x, y in list(b) if issubclass(type(subgrid.get_cell_value(cell_coordinates=(tuple(np.add(pos,(x,y)))))),value)]
    
    positions = [coordinate for x, y in set(b) if issubclass(type(subgrid.get_cell_value(coordinate:=tuple(np.add(pos,(x,y))))),value)]

    return positions

def permutation2(radius: int=1):
    a = list(range(-radius, radius+1))
    b = combinations(a*2, 2)
   
    positions = [coordinate for x, y in set(b) if issubclass(type(subgrid.get_cell_value(coordinate:=tuple(np.add(pos,(x,y))))),value)]

    return positions 

    
# %%
print(numpy())
print(python())
print(numpy2())
print(mixed())
print(permutation())
print(permutation2())

 # %%
import timeit
a = timeit.timeit(numpy, number=10000)
b = timeit.timeit(python, number=10000)
c = timeit.timeit(numpy2, number=10000)
d = timeit.timeit(mixed, number=10000)
e = timeit.timeit(permutation, number=10000)
f = timeit.timeit(permutation2, number=10000)
print(f"numpy: {a} \n python: {b}\n numpy2: {c}\n mixed: {d}\n permutation: {e}\n\n permutation2: {f}")
print(f"best {min([a,b,c,d,e,f])}")
# %%
import numpy as np
from itertools import permutations, combinations

def permutation():
    cells =  set()
    for x in range(-1,2):
        for y in range(-1,2):
            cells.add((x,y))
    return cells

def np_permutation():
    a = [-1,0,1]
    b = combinations(a*2, 2)
    return set(b)
# %%
print(permutation())
print(np_permutation())
# %%
import timeit
a = timeit.timeit(np_permutation, number=10000)
b = timeit.timeit(permutation, number=10000)

print(f"{'numpy:':<10} {a:>10} \n{'python:':<10} {b:>10}")
#%%
def p_range():
    a = list(range(-1,2))
    
def n_range():
    a = list(np.arange(-1,2))
    
a = timeit.timeit(n_range, number=10000)
b = timeit.timeit(p_range, number=10000)

print(f"{'numpy:':<10} {a:>10} \n{'python:':<10} {b:>10}")

#%%
def f_subgrid(radius: int=1):   
    x1, x2, y1, y2 = pos[0] - 1, pos[0] + 2, pos[1] - 1, pos[1] + 2
    return subgrid._subgrid[x1:x2, y1:y2]
    

[x is not None for x in f_subgrid().flatten()]
#%%
radius = 1
a = list(range(-radius,radius+1))
b = combinations(a*2, 2)  



coordinates = [tuple(np.add(pos,(x,y))) for x, y in set(b)]
occupied = [True if subgrid.get_cell_value(coordinate:=tuple(np.add(pos,(x,y)))) else False for x,y in set(b)] 
print(coordinates, occupied)
# %%
###### DATA STRUCTURES ######
from timeit import timeit as time
from random import randint
n = 10000

lst = range(n)
dic = {x: x for x in range(n)}

def loop_through(iterable):
    [x for x in iterable]
        
def loop_list():
    loop_through(lst)

def loop_dict():
    loop_through(dic)
    
def append_list():
    lst = []
    for i in range(n):
        lst.append(i)
        
def append_dict():
    dic = {}
    for i in range(n):
        dic[i] = i 
        
def get_elem(iterable):
    for _ in range(n):
        iterable[randint(0,n-1)]

def get_elem_list():
    get_elem(lst)
    
def get_elem_dict():
    get_elem(dic)

num=1000    
print("LOOP")          
print(f"List: {time(loop_list, number=num)}")
print(f"Dict: {time(loop_dict, number=num)}")

print("APPEND")          
print(f"List: {time(append_list, number=num)}")
print(f"Dict: {time(append_list, number=num)}")

print("RETRIEVE")          
print(f"List: {time(get_elem_list, number=num)}")
print(f"Dict: {time(get_elem_dict, number=num)}")
# %%
#### INPUTS
pos=(1,1)
radius=2
subregion = grid.color_grid.get_sub_region(initial_pos=pos,radius=radius)
subregion


# %%
def sub_region(initial_pos, radius):
    subgrid = grid.color_grid
    x1, x2, y1, y2 = (initial_pos[0] - radius, initial_pos[0] + radius+1,
                    initial_pos[1] - radius, initial_pos[1] + radius+1)
    
    width, height, _ = subgrid.dimensions    
    array = np.full(fill_value=-1, shape=(x2-x1, y2-y1,3))
    left_pad = right_pad = up_pad = down_pad = 0
        
    if x1 < 0:
        left_pad = -x1
        x1=0
    if x2 > width:
        right_pad = x2 - width
        x2 = width
    if y1 < 0:
        up_pad = -y1
        y1 = 0
    if y2 > height:
        down_pad = y2 - height
        y2 = height
    
    subregion = subgrid._subgrid[x1:x2, y1:y2,:]
    
    x_shape,y_shape,z_shape = subregion.shape
    
    for x in range(x_shape):
        for y in range(y_shape):
            array[x+left_pad, y+up_pad] = subregion[x-right_pad,y-down_pad,:]
        
    return array#, (left_pad, right_pad, up_pad, down_pad)
    
pos=(19,2)
radius=2
array=sub_region(initial_pos=pos,radius=radius)
# %%
