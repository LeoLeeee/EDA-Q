"""
Coordinate system management for ion trap chip
"""

class CoordinateSystem:
    """Manages coordinate system transformations and layer positioning"""
    
    def __init__(self, chip_params):
        self.chip_params = chip_params
        self.coord_offset = None
        self._calculate_coordinate_system()
    
    def _calculate_coordinate_system(self):
        """
        Calculate coordinate system offset with the center of the middle chip as the geometric center
        """
        layer_thickness = self.chip_params['layer_thickness']
        layer_gap = self.chip_params['layer_spacing']
        
        # Calculate positions of each layer (in original coordinate system)
        layer1_start = 0
        layer1_end = layer_thickness
        layer2_start = layer_thickness + layer_gap
        layer2_end = 2 * layer_thickness + layer_gap
        layer3_start = 2 * layer_thickness + 2 * layer_gap
        layer3_end = 3 * layer_thickness + 2 * layer_gap
        
        # Calculate center Z coordinate of the middle layer (Layer 2)
        layer2_center_z = (layer2_start + layer2_end) / 2
        
        # Store coordinate offsets (move middle layer center to Z=0)
        self.coord_offset = {
            'z_offset': -layer2_center_z,  # Z-axis offset
            'original_layer_positions': {
                'layer1_start': layer1_start,
                'layer1_end': layer1_end,
                'layer2_start': layer2_start,
                'layer2_end': layer2_end,
                'layer3_start': layer3_start,
                'layer3_end': layer3_end,
            },
            'adjusted_layer_positions': {
                'layer1_start': layer1_start + (-layer2_center_z),
                'layer1_end': layer1_end + (-layer2_center_z),
                'layer2_start': layer2_start + (-layer2_center_z),
                'layer2_end': layer2_end + (-layer2_center_z),
                'layer3_start': layer3_start + (-layer2_center_z),
                'layer3_end': layer3_end + (-layer2_center_z),
            }
        }
    
    def get_adjusted_z(self, z_value):
        """Apply coordinate offset to Z value"""
        return z_value + self.coord_offset['z_offset']
    
    def get_layer_positions(self):
        """Get adjusted layer positions"""
        return self.coord_offset['adjusted_layer_positions']
    
    def get_original_layer_positions(self):
        """Get original layer positions"""
        return self.coord_offset['original_layer_positions']