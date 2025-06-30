############################################################################################
# File Name: readout_cavity_flipchip_no_pad.py
# Description: This file contains the construction code for the readout cavity without pads.
#              Defines the ReadoutCavityFlipchipNoPad class for drawing flip-chip readout cavity geometry.
############################################################################################

import gdspy
import copy
import math
import numpy as np
from addict import Dict
import toolbox
from base.library_base import LibraryBase


class ReadoutCavityFlipchipNoPad(LibraryBase):
    default_options = Dict(
        # Framework
        name="readout1_nopad",  # Readout cavity name
        type="ReadoutCavityFlipchipNoPad",  # Type
        chip="chip0",  # Chip name
        start_pos=(0, 0),  # Starting position
        coupling_length=200,  # Coupling length
        coupling_dist=26.5,  # Coupling distance
        width=10,  # Readout cavity width
        gap=6,  # Gap
        outline=[],  # Outline
        # Geometric parameters
        start_dir="up",  # Starting direction
        height=250,  # Height
        length=3000,  # Total length
        start_length=300,  # Starting length
        space_dist=60,  # Space distance
        radius=30,  # Corner radius
        orientation=90,  # Orientation
        end_seal_height=20  # End seal height
    )

    def __init__(self, options: Dict = None):
        """
        Initializes the ReadoutCavityFlipchipNoPad class.

        Input:
            options: Dictionary containing the parameters for the readout cavity.
        """
        super().__init__(options)
        self.design_length = 0  # 设计总长度（原始输入）
        self.true_length = 0  # 真实总长度（直线+圆弧）
        self.straight_length = 0  # 直线段总长度
        self.arc_length = 0  # 圆弧段总长度
        return

    def calc_general_ops(self):
        """
        Placeholder for future calculations.
        """
        return

    def draw_gds(self):
        """
        Draws the geometric shapes of the ReadoutLine without pads.
        """
        self.lib = gdspy.GdsLibrary()
        gdspy.library.use_current_library = False
        self.cell = self.lib.new_cell(self.name + "_cell")

        # Retrieve parameters without pad-related options
        start_dir = self.start_dir
        orientation = self.orientation
        width = self.width
        gap = self.gap
        start_pos = self.start_pos
        coupling_length = self.coupling_length
        height = self.height
        length = self.length
        space_dist = self.space_dist
        radius = self.radius
        start_length = self.start_length
        end_seal_height = self.end_seal_height  # End seal height parameter

        # Store design length
        self.design_length = length  # 保存设计总长度

        # Number of turns with safe calculation
        space_num = max(0, math.floor(height / space_dist) - 1)

        # Convert to straight-line equivalent length
        length, start_length, coupling_length = self.convert_length(
            length, coupling_length, start_length, corner_num=space_num * 2, corner_radius=radius
        )

        # Calculate segment lengths
        end_length, one_mid_straight = self.calc_length(
            length=length, start_length=start_length, coupling_length=coupling_length,
            space_dist=space_dist, height=height, space_num=space_num
        )

        # Get path points
        pos = self.get_pos(start_dir, start_length, space_num, space_dist,
                           one_mid_straight, end_length, coupling_length)

        # ================ ACCURATE PATH LENGTH CALCULATION ================
        # Initialize path tracking
        total_straight = 0.0
        total_arc = 0.0

        # Calculate straight segments and arcs
        num_points = len(pos)

        # Calculate number of arcs (each corner has one 90° arc)
        arc_count = num_points - 2

        # Calculate arc length (each arc is 90° of circumference)
        total_arc = arc_count * (math.pi * radius / 2)

        # Calculate each straight segment
        for i in range(num_points - 1):
            p1 = np.array(pos[i])
            p2 = np.array(pos[i + 1])
            segment_length = np.linalg.norm(p2 - p1)

            # For corner segments, subtract the "virtual" parts that are replaced by arcs
            if i > 0 and i < num_points - 2:  # All segments between corners
                segment_length -= 2 * radius
            elif i == 0:  # First segment
                segment_length -= radius
            elif i == num_points - 2:  # Last segment
                segment_length -= radius

            total_straight += segment_length
            # For debugging:
            # print(f"Segment {i} length: {segment_length:.3f} um")

        # Calculate total true length
        total_length = total_straight + total_arc

        # Store calculations
        self.straight_length = total_straight
        self.arc_length = total_arc
        self.true_length = total_length

        # Print detailed length information
        print("\n======== PATH LENGTH REPORT ========")
        print(f"Design total length: {self.design_length} um")
        print(f"Number of corners (90° arcs): {arc_count}")
        print(f"Straight segments total: {total_straight:.3f} um")
        print(f"Arcs total length: {total_arc:.3f} um")
        print(f"TRUE TOTAL LENGTH (straight + arcs): {total_length:.3f} um")
        print(
            f"Deviation from design: {abs(total_length - self.design_length):.3f} um ({abs(total_length - self.design_length) / self.design_length * 100:.2f}%)")
        print("===================================\n")
        # ================ END PATH LENGTH CALCULATION ================

        # Save path end point for creating the seal
        end_point = pos[-1]

        # Draw main cavity path
        path = gdspy.FlexPath(pos, width + gap * 2,
                              corners="circular bend",
                              bend_radius=radius).to_polygonset()

        sub_path = gdspy.FlexPath(pos, width,
                                  corners="circular bend",
                                  bend_radius=radius).to_polygonset()

        # Create cavity body
        cavity = gdspy.boolean(path, sub_path, 'not')

        # ==================== Add end seal ====================
        # Create seal rectangle
        seal_width = width + 2 * gap  # Seal width
        seal_rect = gdspy.Rectangle(
            (end_point[0] - seal_width / 2, end_point[1]),  # Bottom-left
            (end_point[0] + seal_width / 2, end_point[1] - end_seal_height)  # Top-right
        )

        # Merge seal into cavity
        cavity = gdspy.boolean(cavity, seal_rect, 'or')

        # Apply rotation and translation
        cavity.rotate(math.radians(orientation), (0, 0))
        cavity.translate(dx=start_pos[0], dy=start_pos[1])

        # Add to cell
        self.cell.add(cavity)
        return

    def calc_space_num(self, deltax, dist):
        """
        Calculates the number of turns that can fit.

        Input:
            deltax: Height
            dist: Distance

        Returns:
            Number of turns (non-negative)
        """
        return max(0, math.floor(deltax / dist) - 1)

    def calc_corner_diff(self, corner_angle, corner_radius):
        """
        Calculates the corner compensation difference.

        Input:
            corner_angle: Corner angle (degrees)
            corner_radius: Corner radius

        Returns:
            Difference value
        """
        diff = 2 * corner_radius * math.tan(math.radians(corner_angle) / 2) - math.radians(corner_angle) * corner_radius
        return diff

    def calc_length(self, length, start_length, coupling_length, space_dist, height, space_num):
        """
        Calculates segment lengths with safe division.

        Input:
            length: Total length
            start_length: Starting length
            coupling_length: Coupling length
            space_dist: Space distance
            height: Height
            space_num: Number of turns

        Returns:
            End length and middle straight length
        """
        end_length = height - space_num * space_dist

        if space_num <= 0:
            one_mid_straight = 0
        else:
            mid_length = length - start_length - coupling_length - end_length
            one_mid_straight = mid_length / space_num - space_dist

        return end_length, one_mid_straight

    def convert_length(self, length, coupling_length, start_length, corner_num, corner_radius):
        """
        Converts to straight-line equivalent length.

        Input:
            length: Total length
            coupling_length: Coupling length
            start_length: Starting length
            corner_num: Number of turns
            corner_radius: Corner radius

        Returns:
            Converted lengths
        """
        corner_diff = self.calc_corner_diff(90, corner_radius)
        length += (2 * corner_num + 2) * corner_diff
        coupling_length += corner_radius
        start_length += corner_radius
        return length, start_length, coupling_length

    def get_pos(self, start_dir, start_length, space_num, space_dist, one_mid_straight, end_length, coupling_length):
        """
        Calculates path points without pad connections.

        Input:
            start_dir: Starting direction
            start_length: Starting length
            space_num: Number of turns
            space_dist: Interval
            one_mid_straight: Middle straight length
            end_length: End length
            coupling_length: Coupling length

        Returns:
            List of path points
        """
        pos = []
        now_p = (0, 0)
        pos.append(now_p)

        now_dir = start_dir
        if now_dir == "up":
            now_p = (0, start_length)
            pos.append(now_p)
            now_dir = "bot"
        else:
            now_p = (0, -start_length)
            pos.append(now_p)
            now_dir = "up"

        for i in range(space_num):
            now_p = (now_p[0] + space_dist, now_p[1])
            pos.append(now_p)
            if now_dir == "up":
                now_p = (now_p[0], now_p[1] + one_mid_straight)
                pos.append(now_p)
                now_dir = "bot"
            else:
                now_p = (now_p[0], now_p[1] - one_mid_straight)
                pos.append(now_p)
                now_dir = "up"

        now_p = (now_p[0] + end_length, now_p[1])
        pos.append(now_p)

        if now_dir == "up":
            now_p = (now_p[0], now_p[1] + coupling_length)
            pos.append(now_p)
        else:
            now_p = (now_p[0], now_p[1] - coupling_length)
            pos.append(now_p)

        return copy.deepcopy(pos)