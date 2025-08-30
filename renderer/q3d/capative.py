import os
import tempfile
import time
import ansys.aedt.core
import gdstk
import math
import pandas as pd

class capacitance():
    def __init__(self ,project = 'project' ,version = '2024.1'):
        """
        Initializes the Eigenmode class.

        Input:
            options: Dict, user-defined parameters for air bridges without a base.

        Output:
            None.
        """
        self.aedt_version = version
        self.non_graphical = False
        self.project = project

        self.q3d = None
        return
    
    def create_q3d_project(self):
        aedt_version = self.aedt_version
        non_graphical = self.non_graphical
        project_name = self.project
        self.q3d = ansys.aedt.core.Q3d(
                project=project_name,
                version=aedt_version,
                non_graphical=non_graphical,
            )
        
    
    def run_q3d_extraction_from_gds(self , gds_name , thickness = [0.007 , 0.008 , 0.009 , 0.01] , basic_material = 'sapphire' , region_material = 'vaccum'):
        
        d = ansys.aedt.core.Desktop(
                version = self.aedt_version,
                non_graphical=self.non_graphical,
                new_desktop=True,
            )
        
        self.create_q3d_project()
        print(111)
        q3d = self.q3d
        def run_q3d_extraction_example(
            start_point,
            dx,
            dy,
            dz,
            num_cores=8,
        ):
            """
            Execute q3d extraction process, including importing GDS, model construction, and frequency scanning.

            Parameters:
            - start_point: Starting coordinate of the model (tuple or list, e.g., (x, y)).
            - dx: Width in the X direction.
            - dy: Width in the Y direction.
            - dz_list: List of heights along the Z axis (e.g., [0.7, 0.8, 0.9]).
            - num_cores: Number of CPU cores to use.
            """
            temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

            # Launch AEDT (automatically if not already started)

            print(f"Starting simulation: dz={dz} mm")
            gds_number = layer
            time.sleep(0.5)

            # Create q3d instance
            '''            q3d = ansys.aedt.core.Q3d(
                project=project_name,
                version=aedt_version,
                non_graphical=non_graphical,
            )'''
            

            # Model operations: union, subtract, create rectangular prism
            try:
                rec0 = q3d.modeler.create_rectangle(ansys.aedt.core.constants.PLANE.XY , [start_point[0] , start_point_1[1] , 0] ,[dx , dy ] , name = 'rectangle0' )
                rec1 = q3d.modeler.create_rectangle(ansys.aedt.core.constants.PLANE.XY , [start_point[0] , start_point_1[1] , 0] ,[dx , dy ] , name = 'rectangle1' )
                q3d.modeler.intersect([rec0 , q3d.modeler._sheets[0]] ,keep_originals=False)
                q3d.modeler.intersect([rec1 , q3d.modeler._sheets[7] ] , keep_originals=False)
                # Difference operation
                
                move_target = [q3d.modeler._sheets[i] for i in range(6 , 11)]
                move_target.append(q3d.modeler._sheets[12])
                q3d.modeler.move(move_target , [0 , 0 , dz])

                # Create two rectangular boxes
                box1 = q3d.modeler.create_box( [start_point[0] , start_point[1] , dz] ,[dx , dy , 0.43] , name = 'Box1' , material = 'sapphire' )
                box2 = q3d.modeler.create_box( [start_point[0] , start_point[1] , 0] ,[dx , dy , -0.43] , name = 'Box2' , material = 'sapphire' )


                # Create region
                region = q3d.modeler.create_region(
                    pad_value= [0 , 0 , 0 , 0 , 1 , 1],
                    pad_type = ['Percentage Offset' ,'Percentage Offset','Percentage Offset','Percentage Offset', 'Absolute Offset' ,'Absolute Offset'],
                    name = 'region'
                )

                q3d.assign_material(region , 'vacuum')

                conduct = q3d.assign_thin_conductor(q3d.modeler._sheets , material = 'pec' , thickness = 150 / 1e6)

                for i in range(len(q3d.modeler._sheets)):
                    q3d.assign_net(q3d.modeler._sheets[i] , net_name = str(q3d.modeler._sheets[i])   )


                # Setup for frequency scan
                def find_resonance(setup_nr):
                    # Setup creation

                    setup_name = f"setup{setup_nr}"
                    setup = q3d.create_setup(setup_name)
                    setup['Adaptive Freq'] =  5 *1e9
                    print((setup.properties))
                    
                    
                    # Analyze the Eigenmode setup
                    q3d.analyze_setup(setup_name, cores=num_cores, use_auto_settings=True)

                    result = q3d.post.available_report_quantities()
                    print(result)
                    #C(signal1_5,rectangle1)
                    data_dict = {}

                    for i in range(len(result)):
                        ans = q3d.post.get_solution_data(
                            expressions = result[i],
                            setup_sweep_name=f"{setup_name} : LastAdaptive",
                        )
                        #print(ans.data_real())
                        final_ans = ans.data_real()[0]
                        row_key = result[i].split('(')[1].split(',')[0]
                        col_key = result[i].split(')')[0].split(',')[1]
                        if row_key not in data_dict:
                            data_dict[row_key] = {}
                        data_dict[row_key][col_key] = final_ans
                    df = pd.DataFrame.from_dict(data_dict, orient='index')

                    df.fillna(0, inplace=True)

                    row_labels = sorted(df.index)
                    col_labels = sorted(df.columns)

                    df = df.reindex(index=row_labels, columns=col_labels, fill_value=0)

                    # 查看结果
                    print(df)
                    return df

                output = find_resonance(1)

            finally:
                # Save and close project
                q3d.save_project()
                #q3d.close()
                temp_folder.cleanup()

        # Release AEDT desktop after all simulations
        def run_q3d_extraction_default(
            layer,
            start_point,
            dx,
            dy,
            dz,
            num_cores=8,
        ):
            """
            Execute q3d extraction process, including importing GDS, model construction, and frequency scanning.

            Parameters:
            - start_point: Starting coordinate of the model (tuple or list, e.g., (x, y)).
            - dx: Width in the X direction.
            - dy: Width in the Y direction.
            - dz_list: List of heights along the Z axis (e.g., [0.7, 0.8, 0.9]).
            - num_cores: Number of CPU cores to use.
            """
            temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")

            # Launch AEDT (automatically if not already started)

            print(f"Starting simulation: dz={dz} mm")
            q3d.import_gds_3d(gds_path, layer, units="mm", import_method=1)
            time.sleep(0.5)
            print(q3d.modeler._sheets)
            my_rec = dict()
            my_box = dict()
            # Model operations: union, subtract, create rectangular prism
            
            for i in range(len(layer)):
                key_rec = f'rec_{i}'
                key_box = f'box_{i}'
                my_rec[key_rec]= q3d.modeler.create_rectangle(ansys.aedt.core.constants.PLANE.XY , [start_point[0] , start_point_1[1] , 0] ,[dx , dy ] , name = 'rectangle0' )
                my_box[key_box] = q3d.modeler.create_box( [start_point[0] , start_point[1] , 0] ,[dx , dy , 0.43] , name = 'Box1' , material = 'sapphire' )
                print(222)
        
            # Create region
            region = q3d.modeler.create_region(
                pad_value= [0 , 0 , 0 , 0 , 1 , 1],
                pad_type = ['Percentage Offset' ,'Percentage Offset','Percentage Offset','Percentage Offset', 'Absolute Offset' ,'Absolute Offset'],
                name = 'region'
            )
            
            q3d.assign_material(region , 'vacuum')

            for value in my_rec.values():
                q3d.modeler._sheets.append(value)

            conduct = q3d.assign_thin_conductor(q3d.modeler._sheets , material = 'pec' , thickness = 150 / 1e6)

            for i in range(len(q3d.modeler._sheets)):
                q3d.assign_net(q3d.modeler._sheets[i] , net_name = str(q3d.modeler._sheets[i])   )


                # Setup for frequency scan
            def find_resonance(setup_nr):
                # Setup creation

                setup_name = f"setup{setup_nr}"
                setup = q3d.create_setup(setup_name)
                setup['Adaptive Freq'] =  5 *1e9
                print((setup.properties))
                
                # Analyze the Eigenmode setup
                q3d.analyze_setup(setup_name, cores=num_cores, use_auto_settings=True)

                result = q3d.post.available_report_quantities()
                print(result)
                #C(signal1_5,rectangle1)
                data_dict = {}

                for i in range(len(result)):
                    ans = q3d.post.get_solution_data(
                        expressions = result[i],
                        setup_sweep_name=f"{setup_name} : LastAdaptive",
                    )
                    #print(ans.data_real())
                    final_ans = ans.data_real()[0]
                    row_key = result[i].split('(')[1].split(',')[0]
                    col_key = result[i].split(')')[0].split(',')[1]
                    if row_key not in data_dict:
                        data_dict[row_key] = {}
                    data_dict[row_key][col_key] = final_ans
                df = pd.DataFrame.from_dict(data_dict, orient='index')

                df.fillna(0, inplace=True)

                row_labels = sorted(df.index)
                col_labels = sorted(df.columns)

                df = df.reindex(index=row_labels, columns=col_labels, fill_value=0)

                # 查看结果
                print(df)
                return df

            output = find_resonance(1)

        
            # Save and close project
            q3d.save_project()
            #q3d.close()
            temp_folder.cleanup()
        
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
        
        def get_transformed_layer(map):
            for k , v in enumerate(map):
                result_dict = {k: (v , 0) for (k, v) in map}
            return (result_dict)
        
        basedir = os.getcwd()
        gds_path = os.path.join(basedir , gds_name)
        library = gdstk.read_gds(gds_path)
        map = library.layers_and_datatypes()

        if len(library.cells) == 1:
            cell = library.cells[0]
            print(f"Cell: {cell.name}")
            #print(cell.area())
            #print(cell.bounding_box())
            print(dir(cell))
            coords = cell.bounding_box()
            result = convert_coords_to_mm_compare(coords)
            start_point_1 =  result[0]
            end_point_1 = result[1]
            dx = end_point_1[0] - start_point_1[0]
            dy = end_point_1[1] - start_point_1[1] 
            layer = get_transformed_layer(map)
            print('layer: ' , layer )
            for i in range(0 , len(thickness)):   
                print(gds_path)
                print(gds_name)
                q3d.import_gds_3d(gds_path, layer, units="mm", import_method=1)
                print(start_point_1)
                run_q3d_extraction_example( start_point_1 , dx , dy ,dz = thickness[i] )

        else :
            merged = dict()
            final_start_point = 0
            final_end_point = 0
            dx_f = 0
            dy_f = 0
            for cell in library.cells:
                print(f"Cell: {cell.name}")
                #print(cell.area())
                #print(cell.bounding_box())
                if(cell.name == 'chip0'):
                    continue
                coords = cell.bounding_box()
                result = convert_coords_to_mm_compare(coords)
                start_point_1 =  result[0]
                end_point_1 = result[1]
                dx = end_point_1[0] - start_point_1[0]
                dy = end_point_1[1] - start_point_1[1] 
                layer = get_transformed_layer(map)
                print('layer: ' , layer )
                q3d.import_gds_3d(gds_path, layer, units="mm", import_method=1)

            print('merged ' , merged)
            print(len(merged))

            for i in range(0 , len(thickness)):   
                print(start_point_1 ,dx , dy)
                run_q3d_extraction_default(merged, start_point_1 , dx , dy ,dz = thickness[i] )


        d.release_desktop()