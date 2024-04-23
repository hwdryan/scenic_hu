import numpy as np
from pprint import pprint
import math


class Requirements:
    """
    Requirements are defined in this class.
    """

    # Class-level attributes (shared among all instances)
    class_attribute = "class_value"

    def __init__(self, logfile):
        # Instance attributes
        dtype = [
            ('Timestep', float),
            ('Id', int),
            ('Role_name', 'U8'),  
            ('Lane_id', int),  
            ('Location_x', float),
            ('Location_y', float),
            ('Location_z', float),
            ('Rotation_pitch', float),
            ('Rotation_yaw', float),
            ('Rotation_roll', float),
            ('Angular_velocity_x', float),
            ('Angular_velocity_y', float),
            ('Angular_velocity_z', float),
            ('Velocity_x', float),
            ('Velocity_y', float),
            ('Velocity_z', float),
            ('Acceleration_x', float),
            ('Acceleration_y', float),
            ('Acceleration_z', float),
            ('Distance2Ego', float)
        ]

        data = np.genfromtxt(logfile, dtype=dtype, delimiter=',', skip_header=1)
        data['Location_y'] = - data['Location_y']
        data['Timestep'] -= data['Timestep'][0] 
        data['Timestep'] = np.round(data['Timestep'],2)
        self.data = data
        targets = set(data['Role_name'])
        targets.remove('ego')
        self.targets = targets
    
    def evaluate(self,**kwargs):
        """
        Evaluate numbers of reqirements, return results.

        Returns:
            Dictionary - requirement:pass/fail
        """
        for value in kwargs.values():
            if value == False:
                kwargs['conclusion'] = False
                return kwargs
        kwargs['conclusion'] = True
        return kwargs


    def collision(self):
        """
        Test case fails if collision.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        # iter all targets
        for target in self.targets:
            target_rows = self.data[self.data['Role_name'] == target]
            if np.any((target_rows['Distance2Ego']<=0)):
                return False
        return True

    def exceed_acceleration(self, arg):
        """
        Test case fails if exceeds rated acceleration.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        acceleration_x = ego_rows['Acceleration_x']
        acceleration_y = ego_rows['Acceleration_y']
        acceleration_z = ego_rows['Acceleration_z']

        acc = np.sqrt(acceleration_x**2 + acceleration_y**2)
        return np.max(acc) <= 10
    
    def minimum_distance(self, arg):
        """
        Test case fails if minimum distance are violated.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        for target in self.targets:
            target_rows = self.data[self.data['Role_name'] == target]
            if np.any((target_rows['Distance2Ego'] < 1.5)):
                return False
        return True
    
    def ego_overtake(self, target_rolename):
        """
        Test case fails if ego overtakes.
        
        NOTE: Assume same heading, same lane for ego and target
        Args:
            target_rolename: String 

        Returns:
            Boolean - fail (False) or succeed (True)
        """
        # assume same heading, same lane
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        target_rows = self.data[self.data['Role_name'] == target_rolename]
        # vehicle coordinates
        ego_c = ego_rows[['Location_x','Location_y','Rotation_yaw',]]
        target_c = target_rows[['Location_x','Location_y','Rotation_yaw']]
        # 
        ego_target_c = transform_points(ego_c, target_c)
        
        if np.any(ego_target_c[:,0]<=0):
            return False
        return True
    
    def safe_lat_distance(self, target_rolename):
        """
        Test case fails if ego violates the safe lateral distance toward front vehicle.
        
        NOTE: Assume same heading, same lane for ego and target
        Args:
            target_rolename: String 

        Returns:
            Boolean - fail (False) or succeed (True)
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        target_rows = self.data[self.data['Role_name'] == target_rolename]
        ego_v = np.sqrt(ego_rows['Velocity_x']**2 + ego_rows['Velocity_y']**2 + ego_rows['Velocity_z']**2)
        distance_2_ego = target_rows['Distance2Ego']


        d_min = []
        for v in ego_v:
            if 0 <= v < 2:
                d_min.append(v*1.0)
            elif 2 <= v < 2.78:
                d_min.append(v*1.1)
            elif 2.78<= v < 5.56 :
                d_min.append(v*1.2)
            elif 5.56 <= v < 8.33:
                d_min.append(v*1.3)
            elif 8.33 <= v < 11.11:
                d_min.append(v*1.4)
            elif 11.11 <= v < 13.89:
                d_min.append(v*1.5)
            elif 13.89 <= v < 16.67:
                d_min.append(v*1.6)

        d_min = np.array(d_min)
        if np.any(distance_2_ego<d_min):
            return False
        return True
    
    
    
        

# Utility functions

def rotate_point(point, angle):
    """Rotate a point around the origin (0, 0) by a given angle in radians."""
    x, y = point
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    rotated_x = x * cos_angle - y * sin_angle
    rotated_y = x * sin_angle + y * cos_angle
    return rotated_x, rotated_y

def transform_points(p1_array, p2_array):
    """Transform points in p2_array from world coordinates to local coordinates of p1_array."""
    transformed_points = []
    for p1, p2 in zip(p1_array, p2_array):
        # Translate p2 to the origin of p1
        translated_x = p2[0] - p1[0]
        translated_y = p2[1] - p1[1]

        # Convert yaw angle from degrees to radians
        yaw_radians = math.radians(p1[2])

        # Rotate p2 around the origin of p1 by the yaw angle of p1
        rotated_x, rotated_y = rotate_point((translated_x, translated_y), yaw_radians)

        transformed_points.append((rotated_x, rotated_y))

    return np.array(transformed_points)