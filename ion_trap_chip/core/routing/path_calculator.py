"""
Routing path calculation for electrode connections
"""

class RoutingPathCalculator:
    """Calculator for routing paths from electrodes to chip edges"""
    
    def __init__(self, coord_system, chip_params, routing_params):
        self.coord_system = coord_system
        self.chip_params = chip_params
        self.routing_params = routing_params
        self.first_turning_points = []
        self.second_turning_points = []
    
    def calculate_first_turning_points(self, extended_point):
        """Calculate first turning point for plane routing"""
        region_key = extended_point['region_key']
        start_x = extended_point['x']
        start_y = extended_point['y']
        layer = extended_point['layer']
        
        slope_dx, slope_dy = self._get_region_slope_direction(region_key)
        
        short_slot_center_x = self.chip_params['short_slot_offset']
        
        if region_key in ['left_top_left', 'left_top_up', 'left_bottom_left', 'left_bottom_down']:
            offset = self.routing_params['left_turning_offset']
            target_x = short_slot_center_x - offset
        else:
            offset = self.routing_params['right_turning_offset']
            target_x = short_slot_center_x + offset
        
        if abs(slope_dx) > 1e-6:
            distance = (target_x - start_x) / slope_dx
            new_y = start_y + slope_dy * distance
        else:
            new_y = start_y
            distance = 0
            target_x = start_x
        
        surface_z = extended_point['z']
        
        return {
            'x': target_x,
            'y': new_y,
            'z': surface_z,
            'layer': layer,
            'electrode_id': extended_point['electrode_id'],
            'region_key': region_key,
            'extended_point_origin': (start_x, start_y, surface_z),
            'slope_direction': (slope_dx, slope_dy),
            'extension_distance': distance,
            'offset_from_short_slot_center': target_x - short_slot_center_x
        }
    
    def calculate_second_turning_points(self, first_turning_point):
        """Calculate second turning point (fan-out point)"""
        region_key = first_turning_point['region_key']
        start_x = first_turning_point['x']
        start_y = first_turning_point['y']
        layer = first_turning_point['layer']
        
        chip_half_length = self.chip_params['base_length'] / 2
        
        if region_key in ['left_top_left', 'left_top_up', 'left_bottom_left', 'left_bottom_down']:
            target_x = -chip_half_length
            new_y = start_y
        else:
            target_x = chip_half_length
            new_y = start_y
        
        surface_z = first_turning_point['z']
        
        return {
            'x': target_x,
            'y': new_y,
            'z': surface_z,
            'layer': layer,
            'electrode_id': first_turning_point['electrode_id'],
            'region_key': region_key,
            'first_turning_point_origin': (start_x, start_y, surface_z),
            'extension_to_chip_edge': True
        }
    
    def calculate_all_turning_points(self, electrode_extended_points):
        """Calculate all turning points"""
        self.first_turning_points = []
        self.second_turning_points = []
        
        for extended_point in electrode_extended_points:
            first_turning_point = self.calculate_first_turning_points(extended_point)
            self.first_turning_points.append(first_turning_point)
            
            second_turning_point = self.calculate_second_turning_points(first_turning_point)
            self.second_turning_points.append(second_turning_point)
            
    def _get_region_slope_direction(self, region_key):
        """
        Determine the extension direction of the beveled edge according to the region key (45-degree direction)
        Returns normalized direction vector (dx, dy)
        """
        import math
        
        sqrt2_inv = 1.0 / math.sqrt(2)  # 1/sqrt(2) ≈ 0.707
        
        if region_key == 'left_top_left':
            # Upper left region: upper left 45-degree direction
            return (-sqrt2_inv, sqrt2_inv)
        elif region_key == 'left_top_up':
            # Upper left region: upper left 45-degree direction  
            return (-sqrt2_inv, sqrt2_inv)
        elif region_key == 'right_top_right':
            # Upper right region: upper right 45-degree direction
            return (sqrt2_inv, sqrt2_inv)
        elif region_key == 'right_top_up':
            # Upper right region: upper right 45-degree direction
            return (sqrt2_inv, sqrt2_inv)
        elif region_key == 'left_bottom_left':
            # Lower left region: lower left 45-degree direction
            return (-sqrt2_inv, -sqrt2_inv)
        elif region_key == 'left_bottom_down':
            # Lower left region: lower left 45-degree direction
            return (-sqrt2_inv, -sqrt2_inv)
        elif region_key == 'right_bottom_right':
            # Lower right region: lower right 45-degree direction
            return (sqrt2_inv, -sqrt2_inv)
        elif region_key == 'right_bottom_down':
            # Lower right region: lower right 45-degree direction
            return (sqrt2_inv, -sqrt2_inv)
        else:
            # Default direction
            return (0, 0)