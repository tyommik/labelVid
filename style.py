def stylesheet(self):
    return """
QSlider::handle:horizontal 
{
background: transparent;
width: 8px;
}
QSlider::groove:horizontal {
border: 1px solid #444444;
height: 8px;
     background: qlineargradient(y1: 0, y2: 1,
                                 stop: 0 #2e3436, stop: 1.0 #000000);
}
QSlider::sub-page:horizontal {
background: qlineargradient( y1: 0, y2: 1,
    stop: 0 #729fcf, stop: 1 #2a82da);
border: 1px solid #777;
height: 8px;
}
QSlider::handle:horizontal:hover {
background: #2a82da;
height: 8px;
width: 8px;
border: 1px solid #2e3436;
}
QSlider::sub-page:horizontal:disabled {
background: #bbbbbb;
border-color: #999999;
}
QSlider::add-page:horizontal:disabled {
background: #2a82da;
border-color: #999999;
}
QSlider::handle:horizontal:disabled {
background: #2a82da;
}
QLineEdit
{
background: black;
color: #585858;
border: 0px solid #076100;
font-size: 8pt;
font-weight: bold;
}
    """
