"""
Basic geometric geometric shape generation utilities
"""
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2

class BaseShapeGenerator:
    """Generator for basic 3D shapes"""
    
    def __init__(self, coord_system):
        self.coord_system = coord_system
    
    def create_box(self, center_x, center_y, z_start, length, width, height):
        """Create a box with specified dimensions"""
        adj_z_start = self.coord_system.get_adjusted_z(z_start)
        
        box_maker = BRepPrimAPI_MakeBox(
            gp_Pnt(center_x - length/2, center_y - width/2, adj_z_start),
            length, width, height
        )
        return box_maker.Shape()
    
    def create_cylinder(self, center_x, center_y, z_start, radius, height):
        """Create a cylinder with specified dimensions"""
        adj_z_start = self.coord_system.get_adjusted_z(z_start)
        
        # Create cylinder axis (Z direction)
        axis = gp_Ax2(gp_Pnt(center_x, center_y, adj_z_start), gp_Dir(0, 0, 1))
        
        # Create cylinder
        cylinder_maker = BRepPrimAPI_MakeCylinder(axis, radius, height)
        return cylinder_maker.Shape()
    
    def create_tapered_pyramid_slot(self, length, width_outer, width_inner, 
                                    center_x=0, center_y=0, z_start=0, z_end=0, 
                                    is_vertical=False):
        """Create tapered pyramid slot"""
        # Apply coordinate offset
        adj_z_start = self.coord_system.get_adjusted_z(z_start)
        adj_z_end = self.coord_system.get_adjusted_z(z_end)
        
        # Create tapered pyramid slot
        if is_vertical:
            # Vertical slot (short slot, along Y direction)
            outer_corners = [
                gp_Pnt(center_x - width_outer/2, center_y - length/2, adj_z_start),
                gp_Pnt(center_x + width_outer/2, center_y - length/2, adj_z_start),
                gp_Pnt(center_x + width_outer/2, center_y + length/2, adj_z_start),
                gp_Pnt(center_x - width_outer/2, center_y + length/2, adj_z_start)
            ]
            inner_corners = [
                gp_Pnt(center_x - width_inner/2, center_y - length/2, adj_z_end),
                gp_Pnt(center_x + width_inner/2, center_y - length/2, adj_z_end),
                gp_Pnt(center_x + width_inner/2, center_y + length/2, adj_z_end),
                gp_Pnt(center_x - width_inner/2, center_y + length/2, adj_z_end)
            ]
        else:
            # Horizontal slot (long slot, along X direction)
            outer_corners = [
                gp_Pnt(center_x - length/2, center_y - width_outer/2, adj_z_start),
                gp_Pnt(center_x + length/2, center_y - width_outer/2, adj_z_start),
                gp_Pnt(center_x + length/2, center_y + width_outer/2, adj_z_start),
                gp_Pnt(center_x - length/2, center_y + width_outer/2, adj_z_start)
            ]
            inner_corners = [
                gp_Pnt(center_x - length/2, center_y - width_inner/2, adj_z_end),
                gp_Pnt(center_x + length/2, center_y - width_inner/2, adj_z_end),
                gp_Pnt(center_x + length/2, center_y + width_inner/2, adj_z_end),
                gp_Pnt(center_x - length/2, center_y + width_inner/2, adj_z_end)
            ]
        
        # Create outer contour
        outer_polygon = BRepBuilderAPI_MakePolygon()
        for corner in outer_corners:
            outer_polygon.Add(corner)
        outer_polygon.Close()
        outer_wire = outer_polygon.Wire()
        
        # Create inner contour  
        inner_polygon = BRepBuilderAPI_MakePolygon()
        for corner in inner_corners:
            inner_polygon.Add(corner)
        inner_polygon.Close()
        inner_wire = inner_polygon.Wire()
        
        # Create tapered pyramid using ThruSections
        loft_maker = BRepOffsetAPI_ThruSections(True)  # True indicates creating a solid
        loft_maker.AddWire(outer_wire)
        loft_maker.AddWire(inner_wire)
        loft_maker.Build()
        
        return loft_maker.Shape()