"""
Chip export utilities
"""

class ChipExporter:
    """Handles chip export functionality"""
    
    def export_to_step(self, chip_shape, filename="ion_trap_chip.step"):
        """Export chip to STEP file"""
        if not chip_shape:
            print("Error: No chip geometry to export")
            return False
        
        try:
            from OCC.Extend.DataExchange import write_step_file
            write_step_file(chip_shape, filename)
            print(f"Chip successfully exported as: {filename}")
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
