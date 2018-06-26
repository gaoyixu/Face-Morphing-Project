import sys
from PyQt5.QtWidgets import QApplication
from ui import *


QSS = '''
* {
    background: #191919;
    color: #DDDDDD;
    border: 1px solid #5A5A5A;
}

QWidget::item:selected {
    background: #3D7848;
}

QCheckBox, QRadioButton{
    border: none;
}

QCheckBox::indicator {
    width: 13px;
    height: 13px;
}

QCheckBox::indicator::unchecked {
    border: 1px solid #5A5A5A;
    background: none;
}

QRadioButton::indicator {
    border: 1px solid #5A5A5A;
    border-radius: 9px;
    background: none;
}

QCheckBox::indicator:unchecked:hover, QRadioButton::indicator:unchecked:hover {
    border: 1px solid #DDDDDD;
}

QCheckBox::indicator::checked, QRadioButton::indicator::checked {
    border: 1px solid #5A5A5A;
    background: #5A5A5A;
}

QCheckBox::indicator:checked:hover, QRadioButton::indicator:checked:hover {
    border: 1px solid #DDDDDD;
    background: #DDDDDD;
}

QAbstractButton:hover {
    background: #353535;
}

QAbstractButton:pressed {
    background: #5A5A5A;
}

QLabel {
    border: none;
}

QLabel#view {
    background-color: #363636;
}

QTableWidget{
    background-color:#3d3d3d;
    color:#fff;
      selection-background-color: #da532c;
    border:solid;
    border-width:3px;
    border-color:#da532c;
}

QHeaderView::section{
    background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 158, 217, 255), stop:1 rgba(36, 158, 217, 255));
    border:none;
    border-top-style:solid;
    border-width:1px;
    border-top-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 158, 217, 255), stop:1 rgba(36, 158, 217, 255));
    color:#fff;
}

QHeaderView{
    background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(20, 158, 217, 255), stop:1 rgba(36, 158, 217, 255));

    border:none;
    border-top-style:solid;
    border-width:1px;
    border-top-color:#149ED9;
    color:#fff;
        font: 75 12pt "Calibri";
}

QTableCornerButton::section{
    border:none;
    background-color:#149ED9;
}
'''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    face_morphing_ui = FaceMorphingUI()
    face_morphing_ui.show()
    sys.exit(app.exec_())
