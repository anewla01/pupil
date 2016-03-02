import os, sys, platform
loc = os.path.abspath(__file__).rsplit('pupil_src', 1)
sys.path.append(os.path.join(loc[0], 'pupil_src', 'shared_modules'))

from calibration_routines.optimization_calibration import  line_line_calibration

import numpy as np
import math
import math_helper
from numpy import array, cross, dot, double, hypot, zeros
from math import acos, atan2, cos, pi, sin, radians
from calibration_routines.visualizer_calibration import *



def almost_equal(a, b, accuracy = 10e-6 ):
    return abs(a - b) < accuracy

if __name__ == '__main__':


    from random import uniform

    cam1_center  = (0,0,0)
    cam1_rotation_quaternion = math_helper.angle_axis2quat( 0 , (0.0,1.0,0.0) )

    cam2_center  = np.array((100,0,0))
    cam2_rotation_quaternion = math_helper.angle_axis2quat( -np.pi/4, (0.0,1.0,0.0) )
    cam2_rotation_matrix = math_helper.quat2mat(cam2_rotation_quaternion)
    random_points = [];
    random_points_amount = 35

    x_var = 20
    y_var = 20
    z_var = 10
    z_min = 100
    for i in range(0,random_points_amount):
        random_point = ( uniform(-x_var,x_var) ,  uniform(-y_var,y_var) ,  uniform(z_min,z_min+z_var)  )
        random_points.append(random_point)


    def toEye(p):
        return np.dot(cam2_rotation_matrix.T, p-cam2_center )

    def toWorld(p):
        return np.dot(cam2_rotation_matrix, p)+cam2_center

    cam1_points = [] #cam1 coords
    cam2_points = [] #cam2 coords
    for p in random_points:
        cam1_points.append(p)
        factor = 0.00 #randomize point in eye space
        pr = p * np.array( (uniform(1.0-factor,1.0+factor),uniform(1.0-factor,1.0+factor),uniform(1.0-factor,1.0+factor))  )
        p2 = toEye(pr) # to cam2 coordinate system
        cam2_points.append(p2)

    sphere_position = (0,0,0)
    initial_rotation = math_helper.angle_axis2quat( -np.pi/4.0, (0.0,1.0,0.0) )
    initial_translation = [c*uniform(1.0,1.0)for c in cam2_center ]


    success, rotation, translation, avg_distance = line_line_calibration( cam1_points, cam2_points , initial_rotation , initial_translation  )
    rotation = np.array(rotation)
    translation = np.array(translation)
    print 'initial rotation: ' , initial_rotation
    print 'initial translation: ' , initial_translation

    print 'true rotation: ' , math_helper.quat2angle_axis(cam2_rotation_quaternion)
    print 'true translation: ' , cam2_center

    print 'found rotation: ' , math_helper.quat2angle_axis(rotation)
    print 'found translation: ' , translation

    print 'avgerage distance: ' , avg_distance

    #replace with the optimized rotation and translation
    cam2_rotation_matrix = math_helper.quat2mat(rotation)
    cam2_transformation_matrix  = np.matrix(np.eye(4))
    cam2_transformation_matrix[:3,:3] = cam2_rotation_matrix
    cam2_translation = np.matrix(translation)
    cam2_translation.shape = (3,1)
    cam2_transformation_matrix[:3,3:4] = cam2_translation

    print cam2_transformation_matrix
    eye = { 'center': (0,0,0), 'radius': 1.0}

    intersection_points_a = [] #world coords
    intersection_points_b = [] #cam2 coords
    avg_error = 0.0
    for a,b in zip(cam1_points , cam2_points): #world coords , cam2 coords

        line_a = (np.array(cam1_center) , np.array(a))
        line_b = (np.array(cam2_center) , toWorld(b) ) #convert to world for intersection
        ai, bi, distance =  math_helper.nearest_intersection_points( line_a , line_b ) #world coords
        avg_error +=distance
        intersection_points_a.append(ai)
        intersection_points_b.append(toEye(bi) )  #cam2 coords , since visualizer expects local coordinates

    avg_error /= len(cam2_points)
    print 'avg error: ', avg_error

    visualizer = Calibration_Visualizer(None,None, intersection_points_a ,cam2_transformation_matrix , intersection_points_b, run_independently = True )
    visualizer.open_window()
    while visualizer.window:
        visualizer.update_window( None, [] , eye)

    print 'Test Ended'


