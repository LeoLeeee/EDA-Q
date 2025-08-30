"""
Chip visualization utilities
"""

class ChipVisualizer:
    """Handles chip visualization"""
    
    def visualize_chip(self, chip_shape):
        """Visualize chip and points"""
        if not chip_shape:
            print("No chip geometry to visualize")
            return
            
        try:
            from OCC.Display.SimpleGui import init_display
        except ImportError:
            print("OpenCASCADE display not available")
            return
        
        display, start_display, add_menu, add_function_to_menu = init_display()
        display.DisplayShape(chip_shape, update=True)
        display.FitAll()
        start_display()
