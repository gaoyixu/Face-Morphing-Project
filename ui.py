"""Front UI for face morphing App.

Author: Yixu Gao 15307130376@fudan.edu.cn

Classes:
    ViewLabel: Label class that can be draw painter on.
    PaintLabel: Label class that can be draw painter on when clicked.
    PointChooseUI: Sub-window to choose the points.
    FaceMorphingUI: Main Window.

P.S: All the names of variables and functions are obvious,
        so the remarks may be less.
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from face_morphing import FaceMorphing
from PyQt5.QtCore import Qt
import os


class ViewLabel(QtWidgets.QLabel):
    """Label class that can be draw painter on."""
    def __init__(self, string):
        super().__init__()
        self.setText(string)
        self.origin_picture = None
        self.show_list = None
        self.show_flag = False
        self.order_flag = False

    def set_picture(self, picture):
        self.origin_picture = picture
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setPixmap(picture.scaled(
            self.size(), Qt.KeepAspectRatio))
        self.setScaledContents(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.show_flag and not self.order_flag:
            painter = QtGui.QPainter()
            painter.begin(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            if type(self.show_list) is list:
                for x, y in self.show_list:
                    painter.drawPoint(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height())
            else:
                for keys in self.show_list:
                    x, y = self.show_list[keys]
                    painter.drawPoint(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height())
        elif self.show_flag and self.order_flag:
            painter = QtGui.QPainter()
            painter.begin(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            if type(self.show_list) is list:
                for i in range(len(self.show_list)):
                    x, y = self.show_list[i]
                    painter.drawPoint(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height())
                    painter.drawText(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height(),
                        str(i))
            else:
                for keys in self.show_list:
                    x, y = self.show_list[keys]
                    painter.drawPoint(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height())
                    painter.drawText(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height(),
                        keys)
        elif self.order_flag and not self.show_flag:
            painter = QtGui.QPainter()
            painter.begin(self)
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
            if type(self.show_list) is list:
                for i in range(len(self.show_list)):
                    x, y = self.show_list[i]
                    painter.drawText(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height(),
                        str(i))
            else:
                for keys in self.show_list:
                    x, y = self.show_list[keys]
                    painter.drawText(
                        x / self.origin_picture.width() * self.width(),
                        y / self.origin_picture.height() * self.height(),
                        keys)
        else:
            return


class PaintLabel(QtWidgets.QLabel):
    """Label class that can be draw painter on when clicked."""
    def __init__(self, picture):
        super().__init__()
        self.src_picture = picture

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setPixmap(picture.scaled(
            self.size(), Qt.KeepAspectRatio))
        self.setScaledContents(True)
        self.clicked_list = []

        self.x = -1
        self.y = -1

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 5))
        for x, y in self.clicked_list:
            painter.drawPoint(x, y)


class PointChooseUI(QtWidgets.QDialog):
    """Sub-window to choose the points."""
    def __init__(self, src_path, dst_path):
        self.src_points = []
        self.dst_points = []
        super().__init__()
        self.setWindowTitle('Choose Points')
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        self.resize(int(screen.width() * 5 / 6), int(screen.height() * 3 / 4))

        main_layout = QtWidgets.QVBoxLayout()

        layout = QtWidgets.QHBoxLayout()
        layout.setStretch(0, 1)
        layout.setStretch(1, 20)
        layout.setStretch(3, 1)

        def clear1():
            table1.clear()
            label1.clicked_list = []
            table1.setRowCount(0)
            label1.repaint()

        layout0 = QtWidgets.QVBoxLayout()
        layout0_up = QtWidgets.QHBoxLayout()
        layout0_up.addWidget(QtWidgets.QLabel('Points'))
        clear_button1 = QtWidgets.QPushButton()
        clear_button1.setText('Clear All')
        clear_button1.resize(clear_button1.sizeHint())
        clear_button1.clicked.connect(clear1)
        layout0_up.addWidget(clear_button1)
        layout0.addLayout(layout0_up)

        table1 = QtWidgets.QTableWidget()
        table1.setColumnCount(2)
        table1.setHorizontalHeaderLabels(['x', 'y'])
        layout0.addWidget(table1)
        layout.addLayout(layout0, 0)

        picture1 = QtGui.QPixmap(src_path)
        picture2 = QtGui.QPixmap(dst_path)

        def get_label1_pixel(event):
            label1.x = event.pos().x()
            label1.y = event.pos().y()
            table1.insertRow(len(label1.clicked_list))
            table1.setItem(len(label1.clicked_list), 0,
                           QtWidgets.QTableWidgetItem(str(label1.x)))
            table1.setItem(len(label1.clicked_list), 1,
                           QtWidgets.QTableWidgetItem(str(label1.y)))
            label1.clicked_list.append((label1.x, label1.y))
            label1.repaint()

        layout1 = QtWidgets.QHBoxLayout()

        label1 = PaintLabel(picture1)
        label1.mousePressEvent = get_label1_pixel
        layout1.addWidget(label1, 0)

        def get_label2_pixel(event):
            label2.x = event.pos().x()
            label2.y = event.pos().y()
            table2.insertRow(len(label2.clicked_list))
            table2.setItem(len(label2.clicked_list), 0,
                           QtWidgets.QTableWidgetItem(str(label2.x)))
            table2.setItem(len(label2.clicked_list), 1,
                           QtWidgets.QTableWidgetItem(str(label2.y)))
            label2.clicked_list.append((label2.x, label2.y))
            label2.repaint()

        label2 = PaintLabel(picture2)
        label2.mousePressEvent = get_label2_pixel

        layout1.addWidget(label2, 1)

        layout.addLayout(layout1, 1)

        def clear2():
            table2.clear()
            label2.clicked_list = []
            table2.setRowCount(0)
            label2.repaint()

        layout2 = QtWidgets.QVBoxLayout()
        layout2_up = QtWidgets.QHBoxLayout()
        layout2_up.addWidget(QtWidgets.QLabel('Points'))
        clear_button2 = QtWidgets.QPushButton()
        clear_button2.setText('Clear All')
        clear_button2.resize(clear_button2.sizeHint())
        clear_button2.clicked.connect(clear2)
        layout2_up.addWidget(clear_button2)
        layout2.addLayout(layout2_up)
        table2 = QtWidgets.QTableWidget()
        table2.setColumnCount(2)
        table2.setHorizontalHeaderLabels(['x', 'y'])
        layout2.addWidget(table2)
        layout.addLayout(layout2, 2)

        def submit_function():
            if len(label1.clicked_list) == 0 or len(label2.clicked_list) == 0:
                QtWidgets.QMessageBox.information(
                    self, "Error",
                    "Please select the points first!")
                return
            if len(label2.clicked_list) != len(label1.clicked_list):
                QtWidgets.QMessageBox.information(
                    self, "Error",
                    "The numbers of points in two pictures must be the same!")
                return
            self.src_points = [(int(x / label1.width() * picture1.width()),
                                int(y / label1.height() * picture1.height()))
                               for x, y in label1.clicked_list]
            self.dst_points = [(int(x / label2.width() * picture2.width()),
                                int(y / label2.height() * picture2.height()))
                               for x, y in label2.clicked_list]
            self.close()

        main_layout.addLayout(layout)
        submit_button = QtWidgets.QPushButton()
        submit_button.setText('Submit')
        submit_button.resize(submit_button.sizeHint())
        main_layout.addWidget(submit_button)
        submit_button.clicked.connect(submit_function)
        self.setLayout(main_layout)
        self.resize(main_layout.sizeHint())


class FaceMorphingUI(QtWidgets.QWidget):
    """Main Window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Face Morphing')
        self.face_morphing = FaceMorphing()
        self.src_path = ''
        self.src_img = None
        self.dst_path = ''
        self.dst_img = None
        self.points_auto_mode = False
        self.manhattan_mode = False
        self.rgb_mode = True
        self.src_points = None
        self.dst_points = None
        self.order_show = False
        self.scatter_show = False
        self.face_flag = False
        self.init_ui()

    def init_ui(self):
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        grid = QtWidgets.QGridLayout()
        grid.setColumnStretch(0, 3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 3)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 4)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 10)
        grid.setRowStretch(2, 3)

        # Path view
        pic1_path_line = QtWidgets.QLineEdit()
        pic1_button = QtWidgets.QPushButton()
        pic1_button.setText('Select Picture')

        pic2_path_line = QtWidgets.QLineEdit()
        pic2_button = QtWidgets.QPushButton()
        pic2_button.setText('Select Picture')

        def choose_src_picture():
            self.src_path, _ = QFileDialog.getOpenFileName(
                None, 'Open Image', os.getcwd(),
                'Image Files (*.png *.jpg *.bmp)')
            pic1_path_line.setText(self.src_path)

            self.face_morphing.set_src_path(self.src_path)
            self.src_img = self.face_morphing.open_src_img()

            if self.src_img:
                pic1_view.setPixmap(
                    QtGui.QPixmap(self.src_path).scaled(pic1_view.width(),
                                                        pic1_view.height()))
                pic1_view.setScaledContents(True)
                pic1_view.set_picture(QtGui.QPixmap(self.src_path))
            else:
                QtWidgets.QMessageBox.information(
                    self, "Error", "Illegal File Path! Select Again!")

        def choose_dst_picture():
            self.dst_path, _ = QFileDialog.getOpenFileName(
                None, 'Open Image', os.getcwd(),
                'Image Files (*.png *.jpg *.bmp)')
            pic2_path_line.setText(self.dst_path)

            self.face_morphing.set_dst_path(self.dst_path)
            self.dst_img = self.face_morphing.open_dst_img()

            if self.dst_img:
                pic2_view.setPixmap(
                    QtGui.QPixmap(self.dst_path).scaled(pic2_view.width(),
                                                        pic2_view.height()))
                pic2_view.setScaledContents(True)
                pic2_view.set_picture(QtGui.QPixmap(self.dst_path))
            else:
                QtWidgets.QMessageBox.information(
                    self, "Error", "Illegal File Path! Select Again!")

        pic1_button.clicked.connect(choose_src_picture)
        pic2_button.clicked.connect(choose_dst_picture)

        grid.addWidget(pic1_path_line, 0, 0)
        grid.addWidget(pic1_button, 0, 1)
        grid.addWidget(pic2_path_line, 0, 2)
        grid.addWidget(pic2_button, 0, 3)

        result_label = QtWidgets.QLabel('Result')
        result_label.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(result_label, 0, 4)

        # Set the graph view
        pic1_view = ViewLabel('Picture To Be Morphed')
        pic1_view.setObjectName('view')
        pic1_view.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(pic1_view, 1, 0, 1, 2)

        pic2_view = ViewLabel('Picture Morphing To')
        pic2_view.setObjectName('view')
        pic2_view.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(pic2_view, 1, 2, 1, 2)

        result_view = ViewLabel('Morphing Result')
        result_view.setObjectName('view')
        result_view.setAlignment(QtCore.Qt.AlignCenter)
        grid.addWidget(result_view, 1, 4, 1, 1)

        # Add points
        add_points_layout = QtWidgets.QGridLayout()

        # Mode choose
        mode_choose_layout = QtWidgets.QGridLayout()
        mode_choose_layout.setColumnStretch(0, 1)
        mode_choose_layout.setColumnStretch(1, 1)
        mode_choose_group = QtWidgets.QButtonGroup(mode_choose_layout)
        manual = QtWidgets.QRadioButton()
        manual.setText('Manually')
        auto = QtWidgets.QRadioButton()
        auto.setText('Automatically')
        manual.clicked.connect(self._set_manual)
        auto.clicked.connect(self._set_auto)
        manual.toggle()

        mode_choose_group.addButton(manual)
        mode_choose_group.addButton(auto)
        manual_layout = QtWidgets.QHBoxLayout()
        manual_layout.addStretch(1)
        manual_layout.addWidget(manual)
        mode_choose_layout.addLayout(manual_layout, 0, 0)
        auto_layout = QtWidgets.QHBoxLayout()
        auto_layout.addWidget(auto)
        auto_layout.addStretch(1)
        mode_choose_layout.addLayout(auto_layout, 0, 1)

        add_points_layout.addLayout(mode_choose_layout, 0, 0)

        # Show
        scatter = QtWidgets.QCheckBox()
        scatter.setText('Show Scatter')
        order = QtWidgets.QCheckBox()
        order.setText('Show Order')

        def show_scatter(state):
            self.scatter_show = True if state == Qt.Checked else False
            if not self.src_points:
                return
            pic1_view.show_flag = True if self.scatter_show else False
            pic2_view.show_flag = True if self.scatter_show else False
            pic1_view.repaint()
            pic2_view.repaint()

        def show_order(state):
            self.order_show = True if state == Qt.Checked else False
            if not self.src_points:
                return
            pic1_view.order_flag = True if self.order_show else False
            pic2_view.order_flag = True if self.order_show else False
            pic1_view.repaint()
            pic2_view.repaint()

        scatter.stateChanged.connect(show_scatter)
        order.stateChanged.connect(show_order)

        show_layout = QtWidgets.QGridLayout()
        show_layout.setColumnStretch(0, 1)
        show_layout.setColumnStretch(1, 1)

        scatter_layout = QtWidgets.QHBoxLayout()
        scatter_layout.addStretch(1)
        scatter_layout.addWidget(scatter)
        show_layout.addLayout(scatter_layout, 0, 0)
        order_layout = QtWidgets.QHBoxLayout()
        order_layout.addWidget(order)
        order_layout.addStretch(1)
        show_layout.addLayout(order_layout, 0, 1)

        add_points_layout.addLayout(show_layout, 1, 0)

        # Add points button
        def add_points_function():
            if not self.src_img or not self.dst_img:
                return
            self.src_points = []
            self.dst_points = []
            if self.points_auto_mode:
                try_src_points = self.face_morphing.auto_select_points(
                    self.src_path)
                try_dst_points = self.face_morphing.auto_select_points(
                    self.dst_path)
                if not try_src_points or not try_dst_points:
                    QtWidgets.QMessageBox.information(
                        self, "Error",
                        "Something Wrong happened! \n"
                        "Maybe the following reasons:\n"
                        "    The Face++ API Broken. \n"
                        "    The face in the picture cannot be recognized. \n"
                        "Please select the points manually.")
                    return
                else:
                    self.src_points = try_src_points
                    self.dst_points = try_dst_points
                    pic1_view.show_list = self.src_points
                    pic2_view.show_list = self.dst_points
                    pic1_view.repaint()
                    pic2_view.repaint()
                    self.face_morphing.flag = False
                    return
            else:
                new_window = PointChooseUI(self.src_path, self.dst_path)
                new_window.exec()
                self.src_points = new_window.src_points
                self.dst_points = new_window.dst_points
                pic1_view.show_list = self.src_points
                pic2_view.show_list = self.dst_points
                pic1_view.repaint()
                pic2_view.repaint()
                self.face_morphing.flag = True
                return

        add_points_button_layout = QtWidgets.QHBoxLayout()
        add_points_button = QtWidgets.QPushButton()
        add_points_button.setText('Add Points')
        add_points_button.setFixedWidth(add_points_button.sizeHint().width())
        add_points_button.clicked.connect(add_points_function)

        add_points_button_layout.addStretch()
        add_points_button_layout.addWidget(add_points_button)
        add_points_button_layout.addStretch()
        add_points_layout.addLayout(add_points_button_layout, 2, 0, 1, 2)

        grid.addLayout(add_points_layout, 2, 0, 1, 4)

        # Morphing box
        morphing_mode_layout = QtWidgets.QGridLayout()
        morphing_mode_layout.setColumnStretch(0, 1)
        morphing_mode_layout.setColumnStretch(1, 1)

        distance_metric_layout = QtWidgets.QVBoxLayout()

        distance_metric_label = QtWidgets.QLabel('Distance Metric:')
        distance_metric_label.setAlignment(QtCore.Qt.AlignCenter)
        distance_metric_group = QtWidgets.QButtonGroup(distance_metric_layout)
        euclid_layout = QtWidgets.QHBoxLayout()
        euclid_layout.addStretch()
        euclid = QtWidgets.QRadioButton()
        euclid.setText('Euclid')
        manhattan_layout = QtWidgets.QHBoxLayout()
        manhattan_layout.addStretch()
        manhattan = QtWidgets.QRadioButton()
        manhattan.setText('Manhattan')

        manhattan.clicked.connect(self._set_manhattan)
        euclid.clicked.connect(self._set_euclid)
        euclid.toggle()

        euclid_layout.addWidget(euclid)
        euclid_layout.addStretch()
        manhattan_layout.addWidget(manhattan)
        manhattan_layout.addStretch()
        distance_metric_group.addButton(euclid)
        distance_metric_group.addButton(manhattan)

        distance_metric_layout.addWidget(distance_metric_label)
        distance_metric_layout.addLayout(euclid_layout)
        distance_metric_layout.addLayout(manhattan_layout)

        color_mode_layout = QtWidgets.QVBoxLayout()

        color_mode_label = QtWidgets.QLabel('Color Mode:')
        color_mode_label.setAlignment(QtCore.Qt.AlignCenter)
        color_mode_group = QtWidgets.QButtonGroup(color_mode_layout)
        rgb_layout = QtWidgets.QHBoxLayout()
        rgb_layout.addStretch()
        rgb = QtWidgets.QRadioButton()
        rgb.setText('RGB')
        gray_layout = QtWidgets.QHBoxLayout()
        gray_layout.addStretch()
        gray = QtWidgets.QRadioButton()
        gray.setText('Gray')

        rgb.clicked.connect(self._set_rgb)
        gray.clicked.connect(self._set_gray)
        rgb.toggle()

        rgb_layout.addWidget(rgb)
        rgb_layout.addStretch()
        gray_layout.addWidget(gray)
        gray_layout.addStretch()
        color_mode_group.addButton(rgb)
        color_mode_group.addButton(gray)

        color_mode_layout.addWidget(color_mode_label)
        color_mode_layout.addLayout(rgb_layout)
        color_mode_layout.addLayout(gray_layout)

        flag_layout = QtWidgets.QVBoxLayout()

        flag_label = QtWidgets.QLabel('Mode:')
        flag_label.setAlignment(QtCore.Qt.AlignCenter)
        flag_group = QtWidgets.QButtonGroup(flag_layout)
        all_layout = QtWidgets.QHBoxLayout()
        all_layout.addStretch()
        all_p = QtWidgets.QRadioButton()
        all_p.setText('All Photo')
        face_layout = QtWidgets.QHBoxLayout()
        face_layout.addStretch()
        face_p = QtWidgets.QRadioButton()
        face_p.setText('Only Face')

        all_p.clicked.connect(self._set_all)
        face_p.clicked.connect(self._set_face)
        all_p.toggle()

        all_layout.addWidget(all_p)
        all_layout.addStretch()
        face_layout.addWidget(face_p)
        face_layout.addStretch()
        flag_group.addButton(all_p)
        flag_group.addButton(face_p)

        flag_layout.addWidget(flag_label)
        flag_layout.addLayout(all_layout)
        flag_layout.addLayout(face_layout)

        morphing_button_layout = QtWidgets.QHBoxLayout()
        morphing_button = QtWidgets.QPushButton()
        morphing_button.setText('Morphing')
        morphing_button.setFixedWidth(morphing_button.sizeHint().width())
        morphing_button_layout.addStretch()
        morphing_button_layout.addWidget(morphing_button)
        morphing_button_layout.addStretch()

        morphing_mode_layout.addLayout(distance_metric_layout, 0, 0)
        morphing_mode_layout.addLayout(color_mode_layout, 0, 1)
        morphing_mode_layout.addLayout(flag_layout, 0, 2)
        morphing_mode_layout.addLayout(morphing_button_layout, 1, 0, 1, 3)
        grid.addLayout(morphing_mode_layout, 2, 4)

        def convert():
            self.face_morphing.src_img = self.src_img
            self.face_morphing.dst_img = self.dst_img
            self.face_morphing.set_points(self.src_points, self.dst_points)
            if not self.src_points or not self.dst_points:
                return
            if self.rgb_mode:
                self.face_morphing.mode = "RGB"
            else:
                self.face_morphing.mode = "gray"
            if self.manhattan_mode:
                self.face_morphing.distance_mode = "Manhattan"
            else:
                self.face_morphing.distance_mode = "Euler"
            self.face_morphing.flag = not self.face_flag
            self.face_morphing.advanced_morphing()
            view_new_img = QtGui.QPixmap(os.path.join(os.getcwd(), 'result.jpg'))
            result_view.setPixmap(
                view_new_img.scaled(result_view.width(), result_view.height()))
            result_view.setScaledContents(True)

        morphing_button.clicked.connect(convert)

        self.setLayout(grid)

    def _set_auto(self):
        self.points_auto_mode = True

    def _set_manual(self):
        self.points_auto_mode = False

    def _set_manhattan(self):
        self.manhattan_mode = True

    def _set_euclid(self):
        self.manhattan_mode = False

    def _set_rgb(self):
        self.rgb_mode = True

    def _set_gray(self):
        self.rgb_mode = False

    def _set_face(self):
        self.face_flag = True

    def _set_all(self):
        self.face_flag = False
