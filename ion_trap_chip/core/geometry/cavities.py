"""
Cavity generation for ion trap structures
"""
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from .base_shapes import BaseShapeGenerator

class CavityGenerator(BaseShapeGenerator):
    """Generator for ion trap cavities"""
    
    def __init__(self, coord_system, chip_params):
        super().__init__(coord_system)
        self.chip_params = chip_params
    
    def create_uniform_slot(self, length, width, center_x=0, center_y=0, 
                           z_start=0, z_end=0, is_vertical=False):
        """Create uniform width slot"""
        thickness = abs(z_end - z_start)
        
        if is_vertical:
            return self.create_box(center_x, center_y, z_start, width, length, thickness)
        else:
            return self.create_box(center_x, center_y, z_start, length, width, thickness)
    
    def create_circular_hole(self, radius, center_x=0, center_y=0, z_start=0, z_end=0):
        """Create circular hole (cylinder)"""
        height = abs(z_end - z_start)
        return self.create_cylinder(center_x, center_y, z_start, radius, height)
    
    def create_all_circular_holes(self):
        """Create all circular holes"""
        circular_config = self.chip_params['circular_holes']
        
        if not circular_config['enabled']:
            return None
        
        radius = circular_config['radius']
        positions = circular_config['positions']
        through_all = circular_config['through_all_layers']
        
        if len(positions) == 0:
            return None
        
        # Use adjusted layer positions
        if through_all:
            layer_positions = self.coord_system.get_layer_positions()
            z_start = layer_positions['layer1_start'] - self.coord_system.coord_offset['z_offset']
            z_end = layer_positions['layer3_end'] - self.coord_system.coord_offset['z_offset']
        else:
            layer_positions = self.coord_system.get_layer_positions()
            z_start = layer_positions['layer1_start'] - self.coord_system.coord_offset['z_offset']
            z_end = layer_positions['layer1_end'] - self.coord_system.coord_offset['z_offset']
        
        all_holes = []
        
        # Create circular hole for each position
        for center_x, center_y in positions:
            hole = self.create_circular_hole(
                radius=radius,
                center_x=center_x,
                center_y=center_y,
                z_start=z_start, 
                z_end=z_end
            )
            
            if hole:
                all_holes.append(hole)
        
        if len(all_holes) == 0:
            return None
        
        # Merge all circular holes
        combined_holes = all_holes[0]
        for i in range(1, len(all_holes)):
            union_maker = BRepAlgoAPI_Fuse(combined_holes, all_holes[i])
            union_maker.Build()
            if union_maker.IsDone():
                combined_holes = union_maker.Shape()
        
        return combined_holes
    
    def create_layered_cavity_structure(self, length, width_surface, width_interface, width_middle,
                                        center_x=0, center_y=0, layer1_start=0, layer1_end=0,
                                        layer2_start=0, layer2_end=0, layer3_start=0, layer3_end=0,
                                        is_vertical=False):
        """Create layered cavity structure for ion trap"""
        params = self.chip_params
        taper_depth = params['layer_thickness'] * params['taper_depth_ratio']
        middle_taper_depth = params['layer_thickness'] * params['middle_taper_depth_ratio']
        
        all_parts = []
        
        # Layer 1 processing
        layer1_taper = self.create_tapered_pyramid_slot(
            length=length,
            width_outer=width_surface,     
            width_inner=width_interface,   
            center_x=center_x, center_y=center_y,
            z_start=layer1_start,          
            z_end=layer1_start + taper_depth,  
            is_vertical=is_vertical
        )
        if layer1_taper:
            all_parts.append(layer1_taper)
        
        if layer1_start + taper_depth < layer1_end:
            layer1_remaining = self.create_uniform_slot(
                length=length,
                width=width_interface,         
                center_x=center_x, center_y=center_y,
                z_start=layer1_start + taper_depth,  
                z_end=layer1_end,              
                is_vertical=is_vertical
            )
            if layer1_remaining:
                all_parts.append(layer1_remaining)
        
        # Layer 2 processing
        main_thickness = params['layer_thickness'] - 2 * middle_taper_depth
        if main_thickness > 0:
            layer2_main = self.create_uniform_slot(
                length=length,
                width=width_middle,
                center_x=center_x, center_y=center_y,
                z_start=layer2_start + middle_taper_depth,
                z_end=layer2_end - middle_taper_depth,
                is_vertical=is_vertical
            )
            if layer2_main:
                all_parts.append(layer2_main)
        
        layer2_top_taper = self.create_tapered_pyramid_slot(
            length=length,
            width_outer=width_surface,     
            width_inner=width_middle,      
            center_x=center_x, center_y=center_y,
            z_start=layer2_start,
            z_end=layer2_start + middle_taper_depth,  
            is_vertical=is_vertical
        )
        if layer2_top_taper:
            all_parts.append(layer2_top_taper)
        
        layer2_bottom_taper = self.create_tapered_pyramid_slot(
            length=length,
            width_outer=width_middle,      
            width_inner=width_surface,     
            center_x=center_x, center_y=center_y,
            z_start=layer2_end - middle_taper_depth,  
            z_end=layer2_end,
            is_vertical=is_vertical
        )
        if layer2_bottom_taper:
            all_parts.append(layer2_bottom_taper)
        
        # Layer 3 processing
        if layer3_start < layer3_end - taper_depth:
            layer3_front = self.create_uniform_slot(
                length=length,
                width=width_interface,         
                center_x=center_x, center_y=center_y,
                z_start=layer3_start,          
                z_end=layer3_end - taper_depth,     
                is_vertical=is_vertical
            )
            if layer3_front:
                all_parts.append(layer3_front)
        
        layer3_taper = self.create_tapered_pyramid_slot(
            length=length,
            width_outer=width_interface,   
            width_inner=width_surface,     
            center_x=center_x, center_y=center_y,
            z_start=layer3_end - taper_depth,  
            z_end=layer3_end,              
            is_vertical=is_vertical
        )
        if layer3_taper:
            all_parts.append(layer3_taper)
        
        # Merge all parts
        if len(all_parts) == 0:
            return None
        
        combined_cavity = all_parts[0]
        for i in range(1, len(all_parts)):
            union_maker = BRepAlgoAPI_Fuse(combined_cavity, all_parts[i])
            union_maker.Build()
            if union_maker.IsDone():
                combined_cavity = union_maker.Shape()
        
        return combined_cavity
