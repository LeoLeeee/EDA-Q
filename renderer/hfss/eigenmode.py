import os
import tempfile
import time
import ansys.aedt.core
import gdstk
import math

class eigenmode():
    def __init__(self):
        """
        Initializes the Eigenmode class.

        Input:
            options: Dict, user-defined parameters for air bridges without a base.

        Output:
            None.
        """
        self.aedt_version = '2024.1'
        self.non_graphical = False
        return
    
    def run_eigenmode_simulation_from_gds(self , gds_name , thickness = [0.007 , 0.008 , 0.009 , 0.01] , basic_material = 'sapphire' , region_material = 'vaccum'):
        d = ansys.aedt.core.Desktop(
                version = self.aedt_version,
                non_graphical=self.non_graphical,
                new_desktop=True,
            )
        def run_eigenmode_simulation(
            gds_path,
            project_name,
            start_point,
            dx,
            dy,
            dz,
            aedt_version="2024.1",
            num_cores=8,
            non_graphical=False,
        ):
            """
            Execute eigenmode simulation process, including importing GDS, model construction, and frequency scanning.

            Parameters:
            - gds_path: Path to the GDS file.
            - project_name: Name of the project.
            - start_point: Starting coordinate of the model (tuple or list, e.g., (x, y)).
            - dx: Width in the X direction.
            - dy: Width in the Y direction.
            - dz_list: List of heights along the Z axis (e.g., [0.7, 0.8, 0.9]).
            - aedt_version: Version of AEDT.
            - num_cores: Number of CPU cores to use.
            - non_graphical: Whether to run in non-graphical mode.
            """
            temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

            # Launch AEDT (automatically if not already started)


            print(f"Starting simulation: dz={dz} mm")
            gds_number = {0: (0, 0)}
            time.sleep(0.5)

            # Create HFSS instance
            hfss = ansys.aedt.core.Hfss(
                project=project_name,
                version=aedt_version,
                non_graphical=non_graphical,
                solution_type="Eigenmode"
            )

            # Import GDS
            hfss.import_gds_3d(gds_path, gds_number, units="mm", import_method=1)

            # Model operations: union, subtract, create rectangular prism
            try:
                hfss.modeler.unite(hfss.modeler._sheets)
                # Create rectangles
                rec0 = hfss.modeler.create_rectangle(
                    ansys.aedt.core.constants.PLANE.XY, [start_point[0], start_point[1], 0], [dx, dy], name='rectangle1'
                )
                # Difference operation
                hfss.modeler.subtract(rec0, hfss.modeler._sheets[0], keep_originals=False)

                # Create two rectangular boxes
                box1 = hfss.modeler.create_box([start_point[0], start_point[1], 0], [dx, dy, -1], name='Box1', material=basic_material)
                box2 = hfss.modeler.create_box([start_point[0], start_point[1], dz], [dx, dy, 1], name='Box2', material=basic_material)
                # Set boundary conditions
                hfss.create_boundary(hfss.BoundaryType.PerfectE, rec0, 'PerfectE')

                # Create region
                region = hfss.modeler.create_region(
                    pad_value=[0, 0, 0, 0, 100, 100],
                    pad_type='Percentage Offset',
                    name='region',
                    material='vacuum'
                )
                hfss.assign_material(region, region_material)

                # Setup for frequency scan
                def find_resonance():
                    setup_name = "setup1"
                    setup = hfss.create_setup(setup_name)
                    setup.props["MinimumFrequency"] = "5 GHz"
                    setup.props["NumModes"] = 1
                    setup.props["ConvergeOnRealFreq"] = True
                    setup.props["MaximumPasses"] = 15
                    setup.props["MinimumPasses"] = 1
                    setup.props["MaxDeltaFreq"] = 0.05

                    hfss.analyze_setup(setup_name, cores=num_cores, use_auto_settings=True)

                    # Retrieve resonance frequencies
                    eigen_q_quantities = hfss.post.available_report_quantities(quantities_category="Eigen Q")
                    eigen_mode_quantities = hfss.post.available_report_quantities()
                    data = {}
                    for i, expression in enumerate(eigen_mode_quantities):
                        eigen_q_value = hfss.post.get_solution_data(
                            expressions=eigen_q_quantities[i],
                            setup_sweep_name=f"{setup_name} : LastAdaptive",
                            report_category="Eigenmode",
                        )
                        eigen_mode_value = hfss.post.get_solution_data(
                            expressions=expression,
                            setup_sweep_name=f"{setup_name} : LastAdaptive",
                            report_category="Eigenmode",
                        )
                        data[i] = [eigen_q_value.data_real()[0], eigen_mode_value.data_real()[0]]
                    return data

                resonance = {}
                output = find_resonance()
                output = list(output.values())
                next_fmin = output[-1][1] / 1e9
                print(f"Resonant frequency (GHz): {next_fmin}")

            finally:
                # Save and close project
                hfss.save_project()
                #hfss.close()
                temp_folder.cleanup()

        # Release AEDT desktop after all simulations
        
        def convert_coords_to_mm_compare(coords):
            def convert_point(p1, p2):
                x1, y1 = p1
                x2, y2 = p2

                # 处理横坐标
                if x1 >= x2:
                    x1_mm = math.ceil(x1 / 1000 * 10) / 10
                    x2_mm = math.floor(x2 / 1000 * 10) / 10
                else:
                    x1_mm = math.floor(x1 / 1000 * 10) / 10
                    x2_mm = math.ceil(x2 / 1000 * 10) / 10

                # 处理纵坐标
                if y1 >= y2:
                    y1_mm = math.ceil(y1 / 1000 * 10) / 10
                    y2_mm = math.floor(y2 / 1000 * 10) / 10
                else:
                    y1_mm = math.floor(y1 / 1000 * 10) / 10
                    y2_mm = math.ceil(y2 / 1000 * 10) / 10

                # 保留一位小数
                return (
                    (round(x1_mm, 1), round(y1_mm, 1)),
                    (round(x2_mm, 1), round(y2_mm, 1))
                )

            p1, p2 = coords
            return convert_point(p1, p2)
        
        basedir = os.getcwd()
        gds_path = os.path.join(basedir , gds_name)
        library = gdstk.read_gds(gds_path)
       
        for cell in library.cells:
            print(f"Cell: {cell.name}")
            #print(cell.area())
            #print(cell.bounding_box())
            coords = cell.bounding_box()
            result = convert_coords_to_mm_compare(coords)
            start_point_1 =  result[0]
            end_point_1 = result[1]
            dx = end_point_1[0] - start_point_1[0]
            dy = end_point_1[1] - start_point_1[1] 
            for i in range(0 , len(thickness)):   
                print(gds_path)
                print(gds_name)
                run_eigenmode_simulation(gds_path ,gds_name.split('.')[0]+'_'+str(thickness[i]), start_point_1 , dx , dy ,dz = thickness[i] )

        d.release_desktop()