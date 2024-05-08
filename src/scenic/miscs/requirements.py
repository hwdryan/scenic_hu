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
    
    def evaluate(self,results:dict):
        """
        Evaluate numbers of reqirements, return results.

        Returns:
            Dictionary - requirement:pass/fail
        """
        for value in results.values():
            if value == False:
                results['conclusion'] = False
                return results
        results['conclusion'] = True
        return results


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

    def exceed_acceleration(self):
        """
        Test case fails if exceeds rated acceleration.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        rated_acceleration = 10

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        acceleration_x = ego_rows['Acceleration_x']
        acceleration_y = ego_rows['Acceleration_y']
        acceleration_z = ego_rows['Acceleration_z']

        acc = np.sqrt(acceleration_x**2 + acceleration_y**2)
        return np.max(acc) <= rated_acceleration
    
    def minimum_distance(self):
        """
        Test case fails if minimum distance are violated.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        minimum_distance = 1.5
        for target in self.targets:
            target_rows = self.data[self.data['Role_name'] == target]
            if np.any((target_rows['Distance2Ego'] < minimum_distance)):
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
        ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
        target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
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
        distance_to_Ego = target_rows['Distance2Ego']


        d_min = []
        for v in ego_v:
            if v in range(0,2):
                d_min.append(v*1.0)
            elif v in range(2,2.78):
                d_min.append(v*1.1)
            elif v in range(2.78,5.56):
                d_min.append(v*1.2)
            elif v in range(5.56,8.33):
                d_min.append(v*1.3)
            elif v in range(8.33,11.11):
                d_min.append(v*1.4)
            elif v in range(11.11,13.89):
                d_min.append(v*1.5)
            elif v in range(13.89,16.67):
                d_min.append(v*1.6)

        d_min = np.array(d_min)
        if np.any(distance_to_Ego<d_min):
            return False
        return True
    
    
    def ego_drive_normally(self):
        """
        Test case fails if ego drive abnormally, as in:
            ego's deceleration < -2m/s
            ego has different lane id
            at the end, ego's distance to destination > 2m.  

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_lane_id = ego_rows['Lane_id']
        ego_rotated_acceleration = rotate_point((ego_rows['Acceleration_x'],ego_rows['Acceleration_y']),ego_rows['Rotation_yaw'])
        max_deceleration = np.min(ego_rotated_acceleration, axis=0)
        #
        if max_deceleration < -2:
            return False
        # 
        if len(set(ego_lane_id))>1:
            return False
        # 

# Utility functions

def rotate_point(points, angles):
    """Rotate a point around the origin (0, 0) by a given angle in radians."""
    # Convert yaw angle from degrees to radians
    print(angles.shape)
    radians = np.radians(angles)
    print(radians.shape)
    xs, ys = points
    cos_angles = np.cos(radians)
    sin_angles = np.sin(radians)
    rotated_x = xs * cos_angles - ys * sin_angles
    rotated_y = xs * sin_angles + ys * cos_angles
    return np.stack((rotated_x, rotated_y), axis=1)

def transform_points(p1_array, p2_array):
    """Transform points in p2_array from world coordinates to local coordinates of p1_array."""
    
    translated_xs = p2_array[:,0] - p1_array[:,0]
    translated_ys = p2_array[:,1] - p1_array[:,1]
    yaw_angles = p1_array[:,2]

    # Rotate p2_array around the origin of p1_array by the yaw angle of p1_array
    transformed_points = rotate_point((translated_xs, translated_ys), yaw_angles)

    return transformed_points