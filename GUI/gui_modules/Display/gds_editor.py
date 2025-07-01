from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect

from OCC.Display.OCCViewer import Viewer3d
from OCC.Core import gp, BRepBuilderAPI, Quantity


class GdsEditor(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # enable Mouse Tracking
        self.setMouseTracking(True)

        # Strong focus
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow)
        self.setAttribute(Qt.WidgetAttribute.WA_PaintOnScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        self.setAutoFillBackground(False)

        # occ 3dviewer
        self._display = Viewer3d()
        self._display.Create(window_handle=int(
            self.winId()), parent=self, create_default_lights=False, display_glinfo=False)
        # background gradient
        self._display.SetModeShaded()
        # fix top view
        self._display.View_Top()
        self._display.set_bg_gradient_color([0, 10, 10], [0, 10, 10])

        self._pan_start_x = None
        self._pan_start_y = None
        self._drawbox = False

        self._move_start_x = None
        self._move_start_y = None

        self._selected_shape = None

    def resizeEvent(self, event):
        super(GdsEditor, self).resizeEvent(event)
        self._display.View.MustBeResized()

    def paintEngine(self):
        return None

    def keyPressEvent(self, event):
        super(GdsEditor, self).keyPressEvent(event)

    def focusInEvent(self, event):
        self._display.Repaint()

    def focusOutEvent(self, event):
        self._display.Repaint()

    def paintEvent(self, event):
        self._display.Context.UpdateCurrentViewer()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom_factor = 1.25 if delta > 0 else 0.75
        self._display.ZoomFactor(zoom_factor)

    def mousePressEvent(self, event):
        # self.setFocus()
        pos = event.pos()
        button = event.button()
        # use left mouse button to pan
        if button == Qt.MouseButton.LeftButton:
            self._pan_start_x = pos.x()
            self._pan_start_y = pos.y()
        elif button == Qt.MouseButton.RightButton:
            self._move_start_x = pos.x()
            self._move_start_y = pos.y()
            self._display.Context.ClearSelected(True)
            self._display.Select(pos.x(), pos.y())
            self._selected_shape = self._display.Context.SelectedInteractive()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        buttons = event.buttons()
        # use left mouse button to pan
        if buttons == Qt.MouseButton.LeftButton:
            dx = pos.x() - self._pan_start_x
            dy = pos.y() - self._pan_start_y
            self._pan_start_x = pos.x()
            self._pan_start_y = pos.y()
            self._display.Pan(dx, -dy)
        if buttons == Qt.MouseButton.RightButton and self._selected_shape:
            # translate view coord to real coord
            view = self._display.View
            v1 = view.Convert(self._move_start_x, self._move_start_y)
            v2 = view.Convert(pos.x(), pos.y())
            move_vec = gp.gp_Vec(
                gp.gp_Pnt(v1[0], v1[1], 0), gp.gp_Pnt(v2[0], v2[1], 0))
            trsf = gp.gp_Trsf()
            trsf.SetTranslation(move_vec)
            self._selected_shape.SetLocalTransformation(
                self._selected_shape.Transformation()*trsf)
            self._display.Context.Update(self._selected_shape, True)

            self._move_start_x = pos.x()
            self._move_start_y = pos.y()
        else:
            self._display.MoveTo(pos.x(), pos.y())

    def mouseReleaseEvent(self, event):
        button = event.button()
        if button == Qt.MouseButton.RightButton:
            self._selected_shape = None
            self._display.Context.ClearSelected(True)

    def showTopoDS(self, component: list):
        for i in component:
            for s in i.shapes:
                self._display.DisplayShape(
                    s, color=Quantity.Quantity_NameOfColor.Quantity_NOC_CORAL, transparency=0.8)
        viewer._display.FitAll()

    def drawSelectBox(self, event):
        tolerance = 2
        pt = event.pos()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return
        self._drawbox = [self.dragStartPosX, self.dragStartPosY, dx, dy]

    def saveImage(self, path: str = None):
        self._display.ExportToImage(path)


if __name__ == "__main__":
    import sys
    import os
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    current_path = os.path.dirname(os.path.abspath(__file__))
    PROJ_PATH = os.path.abspath(os.path.join(
        os.path.dirname(current_path), "../.."))
    sys.path.append(PROJ_PATH)
    from library.qubits import transmon
    from library.coupling_lines import coupling_line_straight
    import gdsocc
    # from api.design import Design

    # design = Design()
    # design.generate_topology(topo_col=32, topo_row=32)
    # design.topology.generate_random_edges(edges_num=1500)
    # design.generate_qubits(
    #     topology=True, qubits_type="Transmon", chip_name="chip0", dist=3000)
    # design.gds.show_svg()

    app = QApplication([])
    viewer = GdsEditor()
    qubit = transmon.Transmon({})
    cpl = coupling_line_straight.CouplingLineStraight({})

    viewer.showTopoDS([qubit.draw_shape(), cpl.draw_shape()])

    viewer.show()
    sys.exit(app.exec_())
