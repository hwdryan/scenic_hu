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
            ('EgoDestination_x', float),
            ('EgoDestination_y', float),
            ('EgoDestination_z', float),
            ('Distance2Ego', float)
        ]

        data = np.genfromtxt(logfile, dtype=dtype, delimiter=',', skip_header=1)
        data['Location_y'] = - data['Location_y']
        data['EgoDestination_y'] = data['EgoDestination_y']
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

    def test(self):
        return type(self.data)

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
        Test case fails if exceeds specified acceleration.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        specified_acceleration = 5

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_rotated_acceleration = rotate_points((ego_rows['Acceleration_x'],ego_rows['Acceleration_y']),ego_rows['Rotation_yaw'])
        # only acceleration, filter out deceleration
        max_acceleration = np.max(ego_rotated_acceleration[:,0].astype(float), axis=0)

        if max_acceleration > specified_acceleration:
            return False
        return True
    
    def minimum_distance(self):
        """
        Test case fails if minimum distance are violated.

        Returns:
            Bool - fail (False) or succeed (True)
        """
        minimum_distance = 1.5
    
        if np.any((self.data['Distance2Ego'] < minimum_distance)):
            return False
        return True
    
    # def ego_overtake(self, target_rolename):
    #     """
    #     Test case fails if ego overtakes.
        
    #     NOTE: Assume same heading, same lane for ego and target
    #     Args:
    #         target_rolename: String 

    #     Returns:
    #         Boolean - fail (False) or succeed (True)
    #     """
    #     # assume same heading, same lane
    #     ego_rows = self.data[self.data['Role_name'] == 'ego']
    #     original_lane_id = ego_rows['Lane_id'][0]
    #     target_rows = self.data[self.data['Role_name'] == target_rolename]
    #     # vehicle coordinates
    #     ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
    #     target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
    #     # target coordinate in ego local coordinate system
    #     transformed_target_c = transform_points(ego_c, target_c)
    #     # if when parallel to target, ego are on neighbor lane, ego overtook
    #     ego_parallel_segment = ego_rows[np.abs(transformed_target_c[:,0].astype(float))<1]
    #     if ego_parallel_segment == 0:
    #         return True
    #     if np.any(ego_parallel_segment['Lane_id']!=original_lane_id):
    #         return False
    #     return True
    
    def safe_longitudinal_distance(self):
        """
        Regulation: While the AD-Vehicle is not at standstill, and operating in speed range up to 60 km/h, 
        the AD-Function shall adapt the speed to adjust the distance to a lead vehicle in the same lane to be 
        equal or greater than the minimum following distance.
        
        Test case fails if ego violates the safe longitudinal distance toward front vehicle.
        
        NOTE: Assume same heading, same lane for ego and target.
        if ego overtakes to the front of target vehicle, test case also fails.

        Returns:
            Boolean - fail (False) or succeed (True)
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
        for target in self.targets:
            target_rows = self.data[self.data['Role_name'] == target]
            # vehicle coordinates
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            # target coordinate in ego local coordinate system
            transformed_target_c = transform_points(ego_c, target_c)
            ego_v = np.sqrt(ego_rows['Velocity_x']**2 + ego_rows['Velocity_y']**2 + ego_rows['Velocity_z']**2)
            # rows where target is lead vehicle, ego speed >0 and <=60km/h
            # in relevant rows, check the ego following distance
            relevant_condition = (transformed_target_c[:,0].astype(float)>0)&(transformed_target_c[:,1].astype(float)>-1)&(transformed_target_c[:,1].astype(float)<1)&(ego_rows['Lane_id']==target_rows['Lane_id'])&(ego_v>0)&(ego_v<=(60/3.6))
            ego_relevant_rows = ego_rows[relevant_condition]
            target_relevant_rows = target_rows[relevant_condition]
            if ego_relevant_rows.size == 0:
                continue
            ego_v = np.sqrt(ego_relevant_rows['Velocity_x']**2 + ego_relevant_rows['Velocity_y']**2 + ego_relevant_rows['Velocity_z']**2)

            distance_to_Ego = target_relevant_rows['Distance2Ego']


            d_min = []
            for v in ego_v:
                if 0 <= v < 2:
                    d_min.append(2)
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
            if np.any(distance_to_Ego<=d_min):
                return False
        return True
    
    def ego_drive_normally(self):
        """
        Test case fails if ego drive abnormally, as in:
            if ego's deceleration < -2m/s &
                ego has different lane id &
                at the end, ego's distance to destination > 10m,
            test case fails.

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_lane_id = ego_rows['Lane_id']
        ego_rotated_acceleration = rotate_points((ego_rows['Acceleration_x'],ego_rows['Acceleration_y']),ego_rows['Rotation_yaw'])

        max_deceleration = np.min(ego_rotated_acceleration[:,0].astype(float), axis=0)

        # ego's deceleration < -2m/s
        if max_deceleration < -2:
            return False
        # ego has different lane id
        if len(set(ego_lane_id))>1:
            return False
        # at the end, ego's distance to destination > 10m.
        # Location_x Location_y	Location_z EgoDestination_x	EgoDestination_y EgoDestination_z
        if two_points_distance((ego_rows["Location_x"][-1],ego_rows["Location_y"][-1]),(ego_rows['EgoDestination_x'][-1],ego_rows['EgoDestination_y'][-1])) > 10:
            return False
        
        return True
        
    def ego_overtake_safe_lateral_distance(self):
        """
        Regulation: When overtaking pedestrians, cyclists or personal light electric vehicles in built-up areas, 
        the AD-Function shall keep at least 1.5 m lateral distance. If necessary, the AD-Function shall wait. 
        At intersections and junctions, the minimum lateral distance of 1.5m to cyclists does not apply, 
        if cyclists have overtaken the AD-Vehicle waiting there on the right or have come to a standstill next to them.
        
        Test case fails if ego violate safe lateral distance when overtaking road users.
        
        Note: assume same lane, same heading 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        # assume same heading, same lane
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        for rolename in self.targets:
            target_rows = self.data[self.data['Role_name'] == rolename]
            # vehicle coordinates
            ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            # target coordinate in ego local coordinate system
            transformed_target_c = transform_points(ego_c, target_c)
            # When ego langitudinal distance < 3 m
            overtake_segment = target_rows['Distance2Ego'][np.abs(transformed_target_c[:,0].astype(float))<3]
            print("***lateral distance: ", overtake_segment)
            # ego lateral distance shall >= 1.5 m
            if np.any(overtake_segment < 1.5):
                return False 
            return True
    
    # def ego_safe_overtake_oncoming_traffic(self, target_rolename):
    #     """
    #     Test case fails if ego overtake when time for manuevor is not enough, given that opposite lane has oncoming traffic
        
    #     Note: assume straight road, on same section of road from start to end , neighbor lane has opposite travel direction

    #     Returns:
    #         Boolean - fail (False) or succeed (True)     
    #     """
    #     s_safe = 10

    #     ego_rows = self.data[self.data['Role_name'] == 'ego']
    #     original_lane_id = ego_rows['Lane_id'][0]
    #     t_maneuvor_span = ego_rows['Timestep'][ego_rows['Lane_id']!=original_lane_id]
    #     # Ego start overtaking
    #     t0 = np.min(t_maneuvor_span)
    #     # Ego finish overtaking
    #     t1 = np.max(t_maneuvor_span)
    #     # Assume only one target for now
    #     target_rows = self.data[(self.data['Role_name'] == target_rolename)]
    #     """
    #     # Basicly to test who reaches the position where ego finishs overtaking first
    #     t1_position = target_rows[target_rows['Timestep']==np.max(t_maneuvor_span)][['Location_x','Location_y']][0]
    #     # The real t2
    #     target_location = target_rows[["Location_x","Location_y"]]
    #     target_to_t1_distance = np.argmin(np.array([two_points_distance(x,t1_position) for x in target_location]))
    #     t2 = target_rows['Timestep'][target_to_t1_distance][0]
    #     """
    #     ego_location = ego_rows[['Location_x','Location_y']]
    #     target_location = target_rows[["Location_x","Location_y"]]
    #     # s_0 = ego position at t0, s_1 = target position at t0
    #     s_0 = ego_location[ego_rows['Timestep']==t0][0]
    #     s_1 = target_location[target_rows['Timestep']==t0][0]
    #     # v_0 = ego velocity at t0, v_1 = target velocity at t0
    #     v_0 = ego_rows[ego_rows['Timestep']==t0][['Velocity_x','Velocity_y']][0]
    #     v_1 = target_rows[target_rows['Timestep']==t0][['Velocity_x','Velocity_y']][0]
    #     # estimated ttc (plus safe distance)
    #     delta_v = v_1-v_0
    #     ttc = (s_1-s_0-s_safe)/math.sqrt(delta_v[0]**2+delta_v[1]**2)
    #     # t_m = estimated time for meneuvor, s_2 = position when ego finish overtaking
    #     # s_2 = ego_location[ego_rows['Timestep']==t1][0]

    #     front_targets_rows = self.data[(self.data['Role_name'] != 'ego') & \
    #                                   (self.data['Role_name'] != target_rolename) & \
    #                                   (self.data['Lane_id']==original_lane_id)]
    #     further_target_rolename= front_targets_rows[front_targets_rows['Distance2Ego']==np.max(front_targets_rows['Distance2Ego'])]['Role_name'][0]
    #     further_target = self.data[(self.data['Role_name'] == further_target_rolename)]
    #     # target coordinate in ego local coordinate system
    #     ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
    #     target_c = np.stack((further_target['Location_x'],further_target['Location_y'],further_target['Rotation_yaw']),axis=1)
    #     s_2 = reverse_transform_points(target_c, np.ones((target_c.shape[0], 2)) * [10.0, 0])[0]
    #     t_m = (s_2-s_0)/math.sqrt(v_0[0]**2+v_0[1]**2)
    #     # 
    #     if t_m >= ttc:
    #         return False
    #     return True
    
    def ego_safe_overtake_higher_speed(self):
        """
        Test case fails if ego overtake when ego speed is not 15% higher than the vehicle's speed being overtaken.
        
        Note: assume straight road, on same section of road from start to end 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        higher_speed = 15 # %

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        original_lane_id = ego_rows['Lane_id'][0]
        # For each target
        for rolename in self.targets:
            target_rows = self.data[(self.data['Role_name'] == rolename) & (self.data['Lane_id']==original_lane_id)]
            if target_rows.size == 0:
                continue
            # vehicle coordinates
            ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            if ego_c.size != target_c.size:
                continue
            # ego coordinate in target local coordinate system
            transformed_ego_c = transform_points(target_c, ego_c)
            # time span for ego overtake
            t_maneuvor_span = ego_rows['Timestep'][(np.abs(transformed_ego_c[:,0])<5)&(transformed_ego_c[:,1]<5)&(transformed_ego_c[:,1]>0)]
            # check if ego overtook this target vehicle
            if t_maneuvor_span.size == 0:
                continue
            # Ego start overtaking
            t0 = np.min(t_maneuvor_span)
            # Ego finish overtaking
            t1 = np.max(t_maneuvor_span)
            # v_0 = ego velocity at t0, v_1 = target velocity at t0
            # s_0 = ego speed at t0, s_1 = target speed at t0
            v_0 = ego_rows[ego_rows['Timestep']==t0][['Velocity_x','Velocity_y']][0]
            s_0 = math.sqrt(v_0[0]**2+v_0[1]**2)
            v_1 = target_rows[target_rows['Timestep']==t0][['Velocity_x','Velocity_y']][0]
            s_1 = math.sqrt(v_1[0]**2+v_1[1]**2)
            try:
                if (s_0-s_1)/s_1 < 0.15:
                    return False
            except ZeroDivisionError:
                continue
        return True
        
    def ego_being_overtaken(self):
        """
        Test case fails if ego increase speed when being overtaken.
        
        Note: assume straight road, on same section of road from start to end 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        t_start = float('inf')
        t_end = 0

        # For each target
        for rolename in self.targets:
            target_rows = self.data[(self.data['Role_name'] == rolename)]
            # vehicle coordinates
            ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            # target coordinate in ego local coordinate system
            transformed_target_c = transform_points(ego_c, target_c)
            # t_0 = target at the left of ego, t_1 = target in front of ego
            t_0 = np.sort(ego_rows['Timestep'][(transformed_target_c[:,0].astype(float)<1)& \
                                       (transformed_target_c[:,0].astype(float)>-1)& \
                                       (transformed_target_c[:,1].astype(float)< 10)& \
                                       (transformed_target_c[:,1].astype(float)> 0)])[0]
            t_1 = np.sort(ego_rows['Timestep'][(transformed_target_c[:,0].astype(float)>0)& \
                                       (transformed_target_c[:,1].astype(float)< 1.5)& \
                                       (transformed_target_c[:,1].astype(float)> 0)])[0]
            if t_0 < t_start:
                t_start = t_0
            if t_1 > t_end:
                t_end = t_1
        overtaken_velocity_start = ego_rows[ego_rows['Timestep']==t_start][['Velocity_x','Velocity_y']]
        overtaken_velocity_start = math.sqrt(overtaken_velocity_start['Velocity_x']**2+overtaken_velocity_start['Velocity_y']**2)
        overtaken_velocity_end = ego_rows[ego_rows['Timestep']==t_end][['Velocity_x','Velocity_y','Rotation_yaw']]
        overtaken_velocity_end = math.sqrt(overtaken_velocity_end['Velocity_x']**2+overtaken_velocity_end['Velocity_y']**2)
        
        # Set print options to suppress scientific notation
        np.set_printoptions(suppress=True)
        print(overtaken_velocity_start, overtaken_velocity_end)
        if overtaken_velocity_end > overtaken_velocity_start:
            return False

        return True
    
    def ego_emergency_braking(self):
        """
        Regulation:In case an unobstructed cyclist crosses, under urban or rural driving conditions, 
        with a lateral speed component of more than 15 km/h in front of the vehicle, 
        the control strategy of the AD-Function may change between collision avoidance and mitigation 
        only if the manufacturer can demonstrate that this increases the safety of the vehicle occupants 
        and the other road users (e.g. by prioritizing braking over an alternative manoeuvre).
        
        Test case fails if ego didn't reduce speed 20 km/h or to 0 km/h, in case a collision cannot be avoided. If avoidable, ego should brake to stop.
        
        Note: assume straight road, on same section of road from start to end, 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        # ego emergency deceleration
        ego_d = -11.58 # m/s2 
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        original_lane_id = ego_rows['Lane_id'][0]
        for target in self.targets:
            target_rows = self.data[(self.data['Role_name'] == target)]
            # vehicle coordinates
            ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            # target coordinate in ego local coordinate system
            transformed_target_c = transform_points(ego_c, target_c)
            # t_0 = target vehicle start overtaking (lane id being the opposite lane)
            try:
                t_0 = np.min(target_rows['Timestep'][np.abs(transformed_target_c[:,1])<=2])
            except ValueError:
                continue
            # v_0 = ego speed at t_0
            v_0 = ego_rows[ego_rows['Timestep']==t_0][['Velocity_x','Velocity_y']][0]
            # v_1 = target speed at t_0
            v_0 = math.sqrt(v_0[0]**2+v_0[1]**2)
            v_1 = target_rows[target_rows['Timestep']==t_0][['Velocity_x','Velocity_y']][0]
            v_1 = math.sqrt(v_1[0]**2+v_1[1]**2)
            # d = longitudial distance to the cyclist at t_0
            condition = ego_rows[ego_rows['Timestep']==t_0]
            print(condition)
            print()
            d = transformed_target_c[:,0][ego_rows['Timestep']==t_0][0]
            if d < 0:
                return True
            d_safe = 3
            # if unavoidable
            if v_0**2/(2*ego_d) > (d - d_safe):
                # v_2 = ego speed when collision happens
                collision_segment = ego_rows[ego_rows['Distance2Ego']==0]
                v_2 = collision_segment[collision_segment['Timestep']==np.min(collision_segment['Timestep'])][['Velocity_x','Velocity_y']][0]
                v_2 = math.sqrt(v_2[0]**2+v_2[1]**2)
                delta_speed = v_2 - v_0
                if delta_speed < 20/3.6 and v_2 > 0.1:
                    return False
            else:
                # v_2 = ego speed when collision happens
                critical_moment = ego_rows[ego_rows['Distance2Ego']==np.min(ego_rows['Distance2Ego'])][0]
                v_2 = critical_moment[['Velocity_x','Velocity_y']]
                v_2 = math.sqrt(v_2[0]**2+v_2[1]**2)
                if v_2 > 0.1:
                    return False
        return True

    def ego_overtaking_on_the_left(self):
        """
        Test case fails if ego didn't overtake from the left side.
        
        Note: assume same lane, same heading 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        # assume same heading, same lane
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        for rolename in self.targets:
            target_rows = self.data[self.data['Role_name'] == rolename]
            # vehicle coordinates
            ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
            target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
            # target coordinate in ego local coordinate system
            transformed_target_c = transform_points(ego_c, target_c)
            # When ego langitudinal distance < 3 m, ego lateral distance > 1.5 m
            overtake_segment = transformed_target_c[np.abs(transformed_target_c[:,0].astype(float))<1]
            if overtake_segment.size == 0:
                continue
            if np.any(overtake_segment[:,1].astype(float) >= 0):
                return False 
            return True

    def ego_safe_deceleration(self):
        """
        Regulation: The AD-Function shall not perform harsh brake without a compelling reason.

        Test case fails if ego's deceleration is lower than threshold.

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        safe_deceleration = -12

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_rotated_acceleration = rotate_points((ego_rows['Acceleration_x'],ego_rows['Acceleration_y']),ego_rows['Rotation_yaw'])

        max_deceleration = np.min(ego_rotated_acceleration[:,0].astype(float), axis=0)
        np.set_printoptions(suppress=True)
        # print("***max_deceleration: ",np.round(ego_rotated_acceleration[:,0][ego_rotated_acceleration[:,0] < 0].astype(float), 2))
        # ego's deceleration < safe_deceleration
        print(max_deceleration)
        if max_deceleration < safe_deceleration:
            return False
        
        return True

    def ego_lane_keeping(self):
        """
        Test case fails if ego deviates to other lanes.

        Note: assume on same section of road from start to end 

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        ego_rows = self.data[self.data['Role_name'] == 'ego']
        ego_lane_id = ego_rows['Lane_id']
        
        # ego has different lane id
        if len(set(ego_lane_id))>1:
            return False
                
        return True

    def ego_reach_destination(self):
        """
        Test case fails if ego doesn't reach the destination.

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        distance_threshold = 8

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        print("***destination distance: ",two_points_distance((ego_rows["Location_x"][-1],\
                                                                ego_rows["Location_y"][-1]),\
                                                                (ego_rows['EgoDestination_x'][-1],\
                                                                ego_rows['EgoDestination_y'][-1])))
        # at the end, ego's distance to destination > 10m.
        if two_points_distance((ego_rows["Location_x"][-1],\
                                ego_rows["Location_y"][-1]),\
                                (ego_rows['EgoDestination_x'][-1],\
                                 ego_rows['EgoDestination_y'][-1])) > distance_threshold:
            return False
                
        return True

    def ego_speed_limit(self):
        """
        Regulation: The AD-Function shall adjust the speed of the AD-Vehicle to applicable speed limits.

        Test case fails if ego's speed exceed the speed limit.

        Returns:
            Boolean - fail (False) or succeed (True)     
        """
        speed_limit = 12

        ego_rows = self.data[self.data['Role_name'] == 'ego']
        v = ego_rows[['Velocity_x','Velocity_y']]
        s = np.sqrt(ego_rows['Velocity_x']**2+ego_rows['Velocity_y']**2)
        if np.any(s > 12):
            return False
                
        return True
    
    # def ego_react_to_pedetrian(self, pedestrian_name):
    #     """
    #     Test case fails if ego didn't stop and wait for the pedestrian.
        
    #     Note: assume straight road, pedestrian walks perpendicular to the road

    #     Returns:
    #         Boolean - fail (False) or succeed (True)     
    #     """
    #     safe_distance = 8

    #     # assume same heading, same lane
    #     ego_rows = self.data[self.data['Role_name'] == 'ego']
    #     target_rows = self.data[(self.data['Role_name'] == pedestrian_name)]
    #     # vehicle coordinates
    #     ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
    #     target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
    #     # target coordinate in ego local coordinate system
    #     transformed_target_c = transform_points(ego_c, target_c)
    #     target_rotated_velocity = rotate_points((target_rows['Velocity_x'],target_rows['Velocity_y']),ego_rows['Rotation_yaw'])
    #     # If ped in front, with lateral speed, might collide consider safe distance
    #     interact_segment_target = target_rows[(transformed_target_c[:,0]>2)&(target_rotated_velocity[:,1]!=0)]
    #     interact_segment_ego = ego_rows[(transformed_target_c[:,0]>2)&(target_rotated_velocity[:,1]!=0)]
    #     # d_long,d_lat,v_e,v_p
    #     d_long = transformed_target_c[(transformed_target_c[:,0]>2)&(target_rotated_velocity[:,1]!=0)][:,1].astype(float) + safe_distance
    #     d_lat = transformed_target_c[(transformed_target_c[:,0]>2)&(target_rotated_velocity[:,1]!=0)][:,0].astype(float)
    #     d_lat_close = d_lat - 1.5
    #     d_lat_far = d_lat + 1.5
    #     v_e = interact_segment_ego[['Velocity_x','Velocity_y']]
    #     s_e = np.sqrt((v_e[:,0]**2+v_e[:,1]**2))
    #     s_e[s_e==0]=0.001
    #     v_p = interact_segment_target[['Velocity_x','Velocity_y']]
    #     s_p = np.sqrt((v_p[:,0]**2+v_p[:,1]**2))
    #     s_p[s_p==0]=0.001
    #     t_e = d_long/s_e
    #     t_p_far = d_lat_far/s_p
    #     t_p_close = d_lat_close/s_p
    #     # diff > 0, pedestrian walk to the point first
    #     if np.any(t_p_close <= t_e < t_p_far):
    #         if np.any(v_e==[0,0]):
    #             return True
    #         else:
    #             return False
    #     else:
    #         return True

    # def ego_slow_down_for_Traffic_jam_on_opposite_lane(self, pedestrian_name):
    #     """
    #     Test case fails if ego didn't stop and wait for the pedestrian.
        
    #     Note: assume straight two-lane road, each lane has opposite traveling direction. 

    #     Returns:
    #         Boolean - fail (False) or succeed (True)     
    #     """
    #     ego_rows = self.data[self.data['Role_name'] == 'ego']
    #     original_lane_id = ego_rows['Lane_id'][0]
    #     target_rolenames = set(self.data['Role_name']).remove('ego')
    #     for rolename in target_rolenames:
    #         target_rows = self.data[(self.data['Role_name'] == rolename) & (self.data['Lane_id']!=original_lane_id)]
    #         if target_rows.size == 0:
    #             continue
    #         # vehicle coordinates
    #         ego_c = np.stack((ego_rows['Location_x'],ego_rows['Location_y'],ego_rows['Rotation_yaw']),axis=1)
    #         target_c = np.stack((target_rows['Location_x'],target_rows['Location_y'],target_rows['Rotation_yaw']),axis=1)
    #         # target coordinate in ego local coordinate system
    #         transformed_target_c = transform_points(ego_c, target_c)
    #         v_e = ego_rows[['Velocity_x','Velocity_y']]
    #         s_e = np.sqrt((v_e[:,0]**2+v_e[:,1]**2))
    #         v_p = target_rows[['Velocity_x','Velocity_y']]
    #         s_p = np.sqrt((v_p[:,0]**2+v_p[:,1]**2))
    #         # When parallel, ego speed should be no higher than target speed + 15
            



# Utility functions

def rotate_points(points, angles):
    """Rotate points around the origin (0, 0) by a given angle in radians."""
    # Convert yaw angle from degrees to radians
    radians = np.radians(angles)
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
    transformed_points = rotate_points((translated_xs, translated_ys), yaw_angles)

    return transformed_points

def reverse_transform_points(p1_array, p2_array):
    """Transform points in p2_array from local coordinates of p1_array to world coordinates."""
    yaw_angles = p1_array[:,2]

    # Rotate p2_array around the origin of p1_array by the -1*yaw angle of p1_array
    transformed_points = rotate_points((p2_array[:,0], p2_array[:,1]), -1*yaw_angles)
    
    translated_xs = transformed_points[:,0] + p1_array[:,0]
    translated_ys = transformed_points[:,1] + p1_array[:,1]

    return np.stack((translated_xs, translated_ys),axis=1)

def two_points_distance(p1,p2):
    d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
    return d

