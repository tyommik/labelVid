try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *


class Timeline(QSlider):

    def __init__(self, title, parent = None):
        super(QSlider, self).__init__(title)
        self.parent = parent
        self.setRange(0, 0)
        self.setToolTip("No video")
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def addAction(self, action):
        pass

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                val = self.pixelPosToRangeValue(event.pos())
                self.setValue(val)
                if self.parent:
                    self.parent.sliderPositionChanged()
                    self.parent.loadFrame(val)
        # if event.type() == QEvent.MouseButtonRelease:
        #     if event.button() == Qt.LeftButton:
        #         val = self.pixelPosToRangeValue(event.pos())
        #         if self.parent:
        #             self.parent.setListWidgetPosition(val)
        if event.type() == QEvent.MouseMove:
            if self.parent.video_cap and self.parent.video_cap.isOpened():
                pos = self.pixelPosToRangeValue(event.pos())
                mtime = QTime(0, 0, 0, 0)
                time_str = mtime.addMSecs(self.parent.video_cap.get_time(pos))
                self.setToolTip(f"{time_str.toString()}|{pos}")
        return super().eventFilter(source, event)


    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1;
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)
