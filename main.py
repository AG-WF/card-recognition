import os
import sys

import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from card_processor import CardProcessor


class CardRecognitionApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.processor = CardProcessor(debug_dir="debug")
        self.image_path = None
        self._label_pixmaps = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("银行卡识别系统")
        self.setMinimumSize(1180, 780)
        self.resize(1260, 820)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 24)
        root.setSpacing(18)

        header = QtWidgets.QFrame()
        header.setObjectName("header")
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setSpacing(16)

        title_wrap = QtWidgets.QVBoxLayout()
        title_wrap.setSpacing(4)
        title = QtWidgets.QLabel("银行卡识别系统")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("选择银行卡图片，查看预处理、候选区域和最终识别结果")
        subtitle.setObjectName("subtitle")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)
        header_layout.addLayout(title_wrap)
        header_layout.addStretch(1)

        self.status_label = QtWidgets.QLabel("等待选择图片")
        self.status_label.setObjectName("statusPill")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        header_layout.addWidget(self.status_label)
        root.addWidget(header)

        body = QtWidgets.QHBoxLayout()
        body.setSpacing(18)
        root.addLayout(body, 1)

        preview_area = QtWidgets.QWidget()
        preview_grid = QtWidgets.QGridLayout(preview_area)
        preview_grid.setContentsMargins(0, 0, 0, 0)
        preview_grid.setHorizontalSpacing(16)
        preview_grid.setVerticalSpacing(16)

        original_card, self.label_original = self.make_image_card("原始图片", "请选择一张银行卡图片")
        preprocess_card, self.label_preprocess = self.make_image_card("灰度增强", "识别后显示预处理效果")
        contour_card, self.label_contour = self.make_image_card("候选区域", "识别后显示定位过程")
        detected_card, self.label_detected = self.make_image_card("检测结果", "识别后显示卡片检测结果")
        roi_card, self.label_roi = self.make_image_card("卡号区域", "识别后显示提取出的卡号区域", compact=True)

        preview_grid.addWidget(original_card, 0, 0)
        preview_grid.addWidget(preprocess_card, 0, 1)
        preview_grid.addWidget(contour_card, 1, 0)
        preview_grid.addWidget(detected_card, 1, 1)
        preview_grid.addWidget(roi_card, 2, 0, 1, 2)
        preview_grid.setColumnStretch(0, 1)
        preview_grid.setColumnStretch(1, 1)
        preview_grid.setRowStretch(0, 1)
        preview_grid.setRowStretch(1, 1)
        preview_grid.setRowStretch(2, 0)
        body.addWidget(preview_area, 1)

        side_panel = QtWidgets.QFrame()
        side_panel.setObjectName("sidePanel")
        side_panel.setFixedWidth(330)
        side_layout = QtWidgets.QVBoxLayout(side_panel)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(14)

        panel_title = QtWidgets.QLabel("操作面板")
        panel_title.setObjectName("panelTitle")
        side_layout.addWidget(panel_title)

        self.btn_select = self.make_button("选择图片", "primary", QtWidgets.QStyle.SP_DialogOpenButton)
        self.btn_select.clicked.connect(self.select_image)
        side_layout.addWidget(self.btn_select)

        self.btn_recognize = self.make_button("开始识别", "accent", QtWidgets.QStyle.SP_MediaPlay)
        self.btn_recognize.clicked.connect(self.run_recognition)
        side_layout.addWidget(self.btn_recognize)

        self.checkbox_debug = QtWidgets.QCheckBox("保存调试图片到 debug 文件夹")
        self.checkbox_debug.setChecked(True)
        side_layout.addWidget(self.checkbox_debug)

        self.btn_open_debug = self.make_button("打开 debug 文件夹", "secondary", QtWidgets.QStyle.SP_DirOpenIcon)
        self.btn_open_debug.clicked.connect(self.open_debug_folder)
        side_layout.addWidget(self.btn_open_debug)

        divider = QtWidgets.QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        side_layout.addWidget(divider)

        result_title = QtWidgets.QLabel("识别结果")
        result_title.setObjectName("sectionTitle")
        side_layout.addWidget(result_title)

        self.result_box = QtWidgets.QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("识别完成后，卡号会显示在这里")
        self.result_box.setMinimumHeight(170)
        side_layout.addWidget(self.result_box)

        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(10)
        self.btn_copy = self.make_button("复制", "secondary", QtWidgets.QStyle.SP_DialogSaveButton)
        self.btn_copy.clicked.connect(self.copy_result)
        action_row.addWidget(self.btn_copy)

        self.btn_clear = self.make_button("清空", "ghost", QtWidgets.QStyle.SP_DialogResetButton)
        self.btn_clear.clicked.connect(self.clear_result)
        action_row.addWidget(self.btn_clear)
        side_layout.addLayout(action_row)
        side_layout.addStretch(1)

        body.addWidget(side_panel)
        self.apply_styles()

    def make_image_card(self, title, hint, compact=False):
        card = QtWidgets.QFrame()
        card.setObjectName("imageCard")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 14)
        card_layout.setSpacing(10)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("cardTitle")
        card_layout.addWidget(title_label)

        image_label = QtWidgets.QLabel(hint)
        image_label.setObjectName("imagePreview")
        image_label.setAlignment(QtCore.Qt.AlignCenter)
        image_label.setWordWrap(True)
        image_label.setMinimumSize(320, 150 if compact else 230)
        image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        card_layout.addWidget(image_label, 1)
        return card, image_label

    def make_button(self, text, kind, icon_name):
        button = QtWidgets.QPushButton(text)
        button.setProperty("kind", kind)
        button.setCursor(QtCore.Qt.PointingHandCursor)
        button.setMinimumHeight(42)
        icon = self.style().standardIcon(icon_name)
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(18, 18))
        return button

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #f4f7fb;
                color: #172033;
                font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
            }
            #header {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            #title {
                font-size: 26px;
                font-weight: 700;
                color: #0f172a;
                background: transparent;
            }
            #subtitle {
                color: #667085;
                background: transparent;
            }
            #statusPill {
                min-width: 120px;
                padding: 8px 14px;
                border-radius: 8px;
                color: #155eef;
                background: #eef4ff;
                border: 1px solid #c7d7fe;
                font-weight: 600;
            }
            #imageCard, #sidePanel {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            #cardTitle, #panelTitle, #sectionTitle {
                background: transparent;
                color: #1d2939;
                font-weight: 700;
            }
            #panelTitle {
                font-size: 18px;
                margin-bottom: 4px;
            }
            #imagePreview {
                background: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 8px;
                color: #98a2b3;
            }
            QPushButton {
                border: 0;
                border-radius: 8px;
                padding: 0 14px;
                font-weight: 700;
            }
            QPushButton[kind="primary"] {
                color: #ffffff;
                background: #2563eb;
            }
            QPushButton[kind="primary"]:hover {
                background: #1d4ed8;
            }
            QPushButton[kind="accent"] {
                color: #ffffff;
                background: #0f766e;
            }
            QPushButton[kind="accent"]:hover {
                background: #0d665f;
            }
            QPushButton[kind="secondary"] {
                color: #1d2939;
                background: #eef2f7;
                border: 1px solid #d0d5dd;
            }
            QPushButton[kind="secondary"]:hover {
                background: #e4eaf2;
            }
            QPushButton[kind="ghost"] {
                color: #475467;
                background: #ffffff;
                border: 1px solid #d0d5dd;
            }
            QPushButton[kind="ghost"]:hover {
                background: #f2f4f7;
            }
            QCheckBox {
                background: transparent;
                color: #475467;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid #98a2b3;
                background: #ffffff;
            }
            QCheckBox::indicator:checked {
                background: #2563eb;
                border: 1px solid #2563eb;
            }
            QTextEdit {
                background: #f8fafc;
                border: 1px solid #d0d5dd;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                color: #0f172a;
            }
            #divider {
                color: #e4e7ec;
                background: #e4e7ec;
                max-height: 1px;
                margin: 8px 0;
            }
            QMessageBox QLabel {
                background: transparent;
            }
            """
        )

    def select_image(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "选择银行卡图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)",
        )
        if fname:
            self.image_path = fname
            self.show_image(self.label_original, fname)
            self.status_label.setText("图片已选择")
            self.result_box.clear()

    def show_image(self, label, path):
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            label.setText("无法加载图片")
            return

        self.set_label_pixmap(label, pixmap)

    def set_label_pixmap(self, label, pixmap):
        self._label_pixmaps[label] = pixmap
        label.setPixmap(
            pixmap.scaled(
                label.size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for label, pixmap in self._label_pixmaps.items():
            if not pixmap.isNull():
                label.setPixmap(
                    pixmap.scaled(
                        label.size(),
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation,
                    )
                )

    def cvimg_to_qpixmap(self, cvimg):
        if cvimg is None or cvimg.size == 0:
            return QtGui.QPixmap()

        cvimg = np.ascontiguousarray(cvimg)
        if len(cvimg.shape) == 2:
            height, width = cvimg.shape
            data = cvimg.tobytes()
            qimg = QtGui.QImage(
                data,
                width,
                height,
                width,
                QtGui.QImage.Format_Grayscale8,
            )
            return QtGui.QPixmap.fromImage(qimg.copy())

        rgb = cv2.cvtColor(cvimg, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        height, width, channels = rgb.shape
        bytes_per_line = channels * width
        data = rgb.tobytes()
        qimg = QtGui.QImage(
            data,
            width,
            height,
            bytes_per_line,
            QtGui.QImage.Format_RGB888,
        )
        return QtGui.QPixmap.fromImage(qimg.copy())

    def run_recognition(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "提示", "请先选择图片")
            return

        self.status_label.setText("正在识别")
        self.btn_recognize.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        try:
            number, steps = self.processor.process(
                self.image_path,
                debug=self.checkbox_debug.isChecked(),
            )
            labels = [
                self.label_original,
                self.label_preprocess,
                self.label_contour,
                self.label_detected,
                self.label_roi,
            ]
            for label, img in zip(labels, steps):
                pixmap = self.cvimg_to_qpixmap(img)
                if not pixmap.isNull():
                    self.set_label_pixmap(label, pixmap)

            if number:
                self.result_box.setText(f"识别结果：\n{number}")
                self.status_label.setText("识别完成")
            else:
                self.result_box.setText("未检测到可信的银行卡号")
                self.status_label.setText("未识别到卡号")
        except Exception as exc:
            self.status_label.setText("识别失败")
            QtWidgets.QMessageBox.critical(self, "错误", f"识别失败：{exc}")
        finally:
            self.btn_recognize.setEnabled(True)

    def open_debug_folder(self):
        path = os.path.abspath(self.processor.debug_dir)
        if os.path.exists(path):
            os.startfile(path)
        else:
            QtWidgets.QMessageBox.information(self, "提示", "debug 文件夹还不存在")

    def clear_result(self):
        self.result_box.clear()
        self.status_label.setText("等待识别")

    def copy_result(self):
        text = self.result_box.toPlainText()
        if text:
            QtWidgets.QApplication.clipboard().setText(text)
            QtWidgets.QMessageBox.information(self, "提示", "识别结果已复制")
        else:
            QtWidgets.QMessageBox.warning(self, "提示", "没有可复制的内容")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CardRecognitionApp()
    window.show()
    sys.exit(app.exec_())
