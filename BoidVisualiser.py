
import arcade
import numpy as np
from math import atan, sin, cos, sqrt

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

use_instancing = False
def setup_batches():
    global shape_list
    shape_list = arcade.ShapeElementList()
    global use_instancing
    use_instancing = True

def draw_flock(flock):
    if use_instancing:
        draw_flock_instanced(flock)
    else:
        for boid in flock.boids_list:
            draw(boid)

def draw_flock_instanced(flock):
    point_list = []
    colour_list = []
    width, height = flock.get_boid_width_and_height()
    half_width = width * 0.5
    colour = flock.get_boid_colour()
    for boid in flock.boids_list:
        x1, y1, x2, y2, x3, y3 = get_triangle_points(boid, height, half_width)
        point_list.append((x1, y1))
        point_list.append((x2, y2))
        point_list.append((x3, y3))
        point_list.append((x3, y3))
        for i in range(4):
            colour_list.append(colour)

    #To batch - there is a create_rectangles_filled_with_colors method but we need to use the rectangles one here. 
    # The fourth point of the rectangle is forced to the same as the third point (not ideal but works)
    # triangles_filled is only for triangle strips (GL_TRIANGLE_STRIP). ref:
    #https://api.arcade.academy/en/2.6.1/_modules/arcade/buffered_draw_commands.html#create_rectangles_filled_with_colors
    #The other option would be to create a subclass of arcade Shape that amended the gl mode but this is much easier and still fast
    shape = arcade.create_rectangles_filled_with_colors(point_list, colour_list)       
    shape_list.append(shape)
    shape_list.draw()
    shape_list.remove(shape)

def get_triangle_points(boid, height = 50, half_width = 4):
    velocity_vector = np.array([boid.vel_x, boid.vel_y])
    position_vector = np.array([boid.x, boid.y])
    velocity_vector_normalised = normalize(velocity_vector)
    triangle_middle_base = position_vector - velocity_vector_normalised * height
    
    #Linear algebra! If we define dx = x2 - x1 and dy = y2 - y1, then the normals are (-dy, dx) and (dy, -dx).
    #P1 = position vector
    #B2 = position vector - velocity = triangle middle base
    #Normal calcs dV = P2 - P1
    #Right base offset = N1 = (-dV[1], dV[0])
    #Left base offset = N2 = (dV[1], -dV[0])
    #Therefore Triangle points = P1, P2 = B2+N1, P3 = B2+N2

    dV = triangle_middle_base - position_vector
    N1 = normalize( np.array((-dV[1], dV[0])) ) * half_width
    N2 = normalize ( np.array((dV[1], -dV[0])) ) * half_width
    
    P2 = triangle_middle_base + N1
    P3 = triangle_middle_base + N2

    return (boid.x, boid.y, P2[0], P2[1], P3[0], P3[1])

def draw(boid) -> None:
    """
    Draw the boid
    """
    x1, y1, x2, y2, x3, y3 = get_triangle_points(boid)
    
    # heading vector
    #arcade.draw_line(boid.x, boid.y, x3, y3, arcade.color.GRAY, 2)
    # Boid - triangle
    arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, boid.colour)
    # draw range rings
    #if boid.debug:
        #arcade.draw_circle_outline(boid.x, boid.y, boid.range_min, (255, 0, 0, 200), 2, 0)
    #arcade.draw_circle_outline(boid.x, boid.y, 5, (255, 200, 200, 200), 2, 0)
