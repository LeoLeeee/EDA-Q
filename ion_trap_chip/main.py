"""离子阱芯片生成器主程序入口"""

from config.chip_parameters import ChipParameters, ElectrodeParameters, RoutingParameters
from core.coordinate_system import CoordinateSystem
from core.chip_builder import IonTrapChipBuilder
from utils.visualization import visualize_chip_with_points
from utils.export import export_to_step

class IonTrapChipGenerator:
    """离子阱芯片生成器主类"""
    
    def __init__(self):
        # 初始化参数配置
        self.chip_params = ChipParameters()
        self.electrode_params = ElectrodeParameters()
        self.routing_params = RoutingParameters()
        
        # 初始化坐标系统
        self.coord_system = CoordinateSystem(self.chip_params)
        
        # 初始化芯片构建器
        self.chip_builder = IonTrapChipBuilder(
            self.chip_params,
            self.electrode_params,
            self.routing_params,
            self.coord_system
        )
        
        # 存储生成的芯片
        self._generated_chip = None
    
    def generate_chip(self):
        """生成完整的离子阱芯片"""
        print("开始生成离子阱芯片...")
        
        self._generated_chip = self.chip_builder.build_complete_chip()
        
        if self._generated_chip:
            print("芯片生成完成！")
        else:
            print("芯片生成失败！")
        
        return self._generated_chip
    
    def visualize(self):
        """可视化生成的芯片"""
        if not self._generated_chip:
            print("正在生成芯片用于可视化...")
            self.generate_chip()
        
        if self._generated_chip:
            # 收集所有标记点用于可视化
            points_data = self._collect_visualization_points()
            visualize_chip_with_points(self._generated_chip, points_data)
        else:
            print("无法可视化：芯片生成失败")
    
    def export(self, filename="ion_trap_chip.step", format="step"):
        """导出芯片到文件"""
        if not self._generated_chip:
            print("正在生成芯片用于导出...")
            self.generate_chip()
        
        if self._generated_chip:
            if format.lower() == "step":
                return export_to_step(self._generated_chip, filename)
            else:
                print(f"不支持的格式: {format}")
                return False
        else:
            print("无法导出：芯片生成失败")
            return False
    
    def _collect_visualization_points(self):
        """收集用于可视化的所有标记点"""
        points_data = {
            'electrode_corners': self.chip_builder.electrode_builder.electrode_corner_points,
            'extended_points': self.chip_builder.electrode_builder.electrode_extended_points,
            'first_turning_points': self.chip_builder.path_calculator.first_turning_points,
            'second_turning_points': self.chip_builder.path_calculator.second_turning_points,
        }
        return points_data
    
    def print_chip_info(self):
        """打印芯片基本信息"""
        print("\n=== 离子阱芯片参数信息 ===")
        print(f"基板尺寸: {self.chip_params.base_length} × {self.chip_params.base_width} mm")
        print(f"层厚度: {self.chip_params.layer_thickness} mm")
        print(f"长槽尺寸: {self.chip_params.trap_long_length} × {self.chip_params.trap_long_width_surface} mm")
        print(f"短槽尺寸: {self.chip_params.trap_short_length} × {self.chip_params.trap_short_width_surface} mm")
        # 修复：从electrode_params获取电极参数
        print(f"电极尺寸: {self.electrode_params.electrode_width} × {self.electrode_params.gap_width} mm")
        print(f"电极深度: {self.electrode_params.electrode_depth} mm")
        
        total_electrodes = sum(self.electrode_params.region_counts.values())
        print(f"总电极数量: {total_electrodes}")
        print("各区域电极分布:")
        for region, count in self.electrode_params.region_counts.items():
            print(f"  {region}: {count} 个")
        
        # 添加圆形镂空信息
        if self.chip_params.circular_holes['enabled']:
            print(f"圆形镂空: 半径 {self.chip_params.circular_holes['radius']} mm")
            print(f"圆形镂空位置: {self.chip_params.circular_holes['positions']}")

