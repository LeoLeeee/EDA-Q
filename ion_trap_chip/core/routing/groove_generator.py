"""
Groove generation for routing paths
"""
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.gp import gp_Pnt

class GrooveGenerator:
    """Generator for routing grooves"""
    
    def __init__(self, routing_params):
        self.routing_params = routing_params
    
    def create_quadrilateral_prism(self, quadrilateral_points):
        """Create quadrilateral prism with Z-axis displacement"""
        chamfer_offset = self.routing_params['chamfer_offset']
        
        original_points = []
        for point in quadrilateral_points:
            original_points.append(gp_Pnt(point['x'], point['y'], point['z']))
        
        displaced_points = []
        for point in quadrilateral_points:
            current_z = point['z']
            if current_z > 0:
                new_z = current_z - chamfer_offset
            elif current_z < 0:
                new_z = current_z + chamfer_offset
            else:
                new_z = current_z
                
            displaced_points.append(gp_Pnt(point['x'], point['y'], new_z))
        
        original_polygon = BRepBuilderAPI_MakePolygon()
        for point in original_points:
            original_polygon.Add(point)
        original_polygon.Close()
        original_wire = original_polygon.Wire()
        
        displaced_polygon = BRepBuilderAPI_MakePolygon()
        for point in displaced_points:
            displaced_polygon.Add(point)
        displaced_polygon.Close()
        displaced_wire = displaced_polygon.Wire()
        
        loft_maker = BRepOffsetAPI_ThruSections(True)
        loft_maker.AddWire(original_wire)
        loft_maker.AddWire(displaced_wire)
        loft_maker.Build()
        
        if loft_maker.IsDone():
            return loft_maker.Shape()
        else:
            return None
    
    def group_points_by_electrode_and_layer(self, corner_points, extended_points):
        """Group points by electrode ID and layer for parallelograms"""
        grouped_parallelograms = {}
        electrode_layer_groups = {}
        
        for corner_point in corner_points:
            electrode_id = corner_point['electrode_id']
            layer = corner_point['layer']
            key = f"{electrode_id}_{layer}"
            
            if key not in electrode_layer_groups:
                electrode_layer_groups[key] = {
                    'corner_points': [],
                    'extended_points': []
                }
            electrode_layer_groups[key]['corner_points'].append(corner_point)
        
        for extended_point in extended_points:
            electrode_id = extended_point['electrode_id']
            layer = extended_point['layer']
            key = f"{electrode_id}_{layer}"
            
            if key not in electrode_layer_groups:
                electrode_layer_groups[key] = {
                    'corner_points': [],
                    'extended_points': []
                }
            electrode_layer_groups[key]['extended_points'].append(extended_point)
        
        for key, group in electrode_layer_groups.items():
            corner_points = group['corner_points']
            extended_points = group['extended_points']
            
            if len(corner_points) == 2 and len(extended_points) == 2:
                parallelogram_points = [
                    corner_points[0],   
                    extended_points[0], 
                    extended_points[1],
                    corner_points[1],   
                ]
                
                grouped_parallelograms[key] = parallelogram_points
        
        return grouped_parallelograms
    
    def group_plane_routing_quadrilaterals(self, first_points, second_points):
        """Group plane routing points into quadrilaterals"""
        grouped_quadrilaterals = {}
        electrode_layer_groups = {}
        
        for point in first_points:
            electrode_id = point['electrode_id']
            layer = point['layer']
            key = f"{electrode_id}_{layer}"
            
            if key not in electrode_layer_groups:
                electrode_layer_groups[key] = {
                    'first_points': [],
                    'second_points': []
                }
            electrode_layer_groups[key]['first_points'].append(point)
        
        for point in second_points:
            electrode_id = point['electrode_id']
            layer = point['layer']
            key = f"{electrode_id}_{layer}"
            
            if key not in electrode_layer_groups:
                electrode_layer_groups[key] = {
                    'first_points': [],
                    'second_points': []
                }
            electrode_layer_groups[key]['second_points'].append(point)
        
        for key, group in electrode_layer_groups.items():
            first_points = group['first_points']
            second_points = group['second_points']
            
            if len(first_points) == 2 and len(second_points) == 2:
                quadrilateral_points = [
                    first_points[0], 
                    second_points[0], 
                    second_points[1], 
                    first_points[1],  
                ]
                
                grouped_quadrilaterals[key] = quadrilateral_points
        
        return grouped_quadrilaterals
    
    def create_all_routing_grooves(self, corner_points, extended_points):
        """Create all routing grooves"""
        parallelogram_groups = self.group_points_by_electrode_and_layer(corner_points, extended_points)
        
        if len(parallelogram_groups) == 0:
            return None
        
        all_routing_prisms = []
        
        for key, parallelogram_points in parallelogram_groups.items():
            routing_prism = self.create_quadrilateral_prism(parallelogram_points)
            if routing_prism:
                all_routing_prisms.append(routing_prism)
        
        if len(all_routing_prisms) == 0:
            return None
        
        combined_prisms = all_routing_prisms[0]
        for i in range(1, len(all_routing_prisms)):
            union_maker = BRepAlgoAPI_Fuse(combined_prisms, all_routing_prisms[i])
            union_maker.Build()
            if union_maker.IsDone():
                combined_prisms = union_maker.Shape()
        
        return combined_prisms
    
    def create_plane_routing_grooves(self, first_points, second_points):
        """Create plane routing grooves between two sets of points"""
        quadrilateral_groups = self.group_plane_routing_quadrilaterals(first_points, second_points)
        
        if len(quadrilateral_groups) == 0:
            return None
        
        all_prisms = []
        
        for key, quadrilateral_points in quadrilateral_groups.items():
            prism = self.create_quadrilateral_prism(quadrilateral_points)
            if prism:
                all_prisms.append(prism)
        
        if len(all_prisms) == 0:
            return None
        
        combined_prisms = all_prisms[0]
        for i in range(1, len(all_prisms)):
            union_maker = BRepAlgoAPI_Fuse(combined_prisms, all_prisms[i])
            union_maker.Build()
            if union_maker.IsDone():
                combined_prisms = union_maker.Shape()
        
        return combined_prisms
