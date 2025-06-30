# 导入必要的库
import gdspy
from library.readout_lines.readout_cavity_flipchip_no_pad import ReadoutCavityFlipchipNoPad
# 创建一个实例
options = {
    'name': 'readout1_nopad',  # 读出腔名称
    'chip': 'chip0',  # 芯片名称
    'start_pos': (0, 0),  # 起始位置
    'coupling_length': 300,  # 耦合长度
    'coupling_dist': 40,  # 耦合距离
    'width': 10,  # 读出腔宽度
    'gap': 6,  # 间隙
    'start_dir': 'up',  # 起始方向
    'height': 400,  # 高度
    'length': 3000,  # 总长度
    'start_length':400,  # 起始长度
    'space_dist': 60,  # 间距距离
    'radius': 30,  # 圆角半径
    'orientation': 90,  # 方向
    'end_seal_height': 20  # 末端封盖高度
}

# 创建 ReadoutCavityFlipchipNoPad 实例
readout_cavity = ReadoutCavityFlipchipNoPad(options)

# 绘制读出腔的几何结构
readout_cavity.draw_gds()

# 保存生成的 GDS 文件
readout_cavity.lib.write_gds('readout_cavity.gds')

# 输出一些调试信息
print("GDS file 'readout_cavity.gds' has been generated.")