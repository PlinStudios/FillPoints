from krita import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from .fillC import fill,extra_expand

class FillPointsDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ply's Fill Points")

        self.main_widget = QWidget(self)
        self.setWidget(self.main_widget)

        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)

        self.line_input = QLineEdit("Line")
        self.color_point_input = QLineEdit("FillPoints")
        self.color_output_input = QLineEdit("Color")
        self.copy_input = QLineEdit("FillPoints")

        layout.addWidget(QLabel("Line Layer:"))
        layout.addWidget(self.line_input)
        layout.addWidget(QLabel("FillPoints Layer:"))
        layout.addWidget(self.color_point_input)
        layout.addWidget(QLabel("Output Layer:"))
        layout.addWidget(self.color_output_input)

        #config
        layout.addWidget(QLabel("Line Opacity Threshold:"))
        self.opacity_threshold = QSpinBox()
        self.opacity_threshold.setRange(0,255)
        self.opacity_threshold.setSingleStep(1)
        self.opacity_threshold.setValue(255)
        layout.addWidget(self.opacity_threshold)

        layout.addWidget(QLabel("Extra Expansion:"))
        self.expansion = QSpinBox()
        self.expansion.setRange(0,40)
        self.expansion.setSingleStep(1)
        self.expansion.setValue(0)
        layout.addWidget(self.expansion)

        #button to fill
        self.add_btn = QPushButton("Fill")
        layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.fill_frame)
        
        self.anim_start = QLineEdit("0")
        self.anim_end = QLineEdit("100")
        self.anim_start.setValidator(QIntValidator(0, 9999, self))
        self.anim_end.setValidator(QIntValidator(0, 9999, self))
        #animation
        layout.addWidget(QLabel("---Animation---"))
        layout.addWidget(QLabel("start:"))
        layout.addWidget(self.anim_start)
        layout.addWidget(QLabel("end:"))
        layout.addWidget(self.anim_end)
        
        layout.addWidget(QLabel("Copy frames from:"))
        layout.addWidget(self.copy_input)

        self.add_btn = QPushButton("Fill Animation")
        layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.fill_animation)

    def fill_frame(self):
        doc = Krita.instance().activeDocument()
        if doc is None:
            return
        
        active_node = doc.activeNode()

        r = self.getLayers(doc)
        if r==None:
            return
        line_node,point_node,color_node,x,y,w,h = r

        #get pixel data
        linedata = line_node.pixelData(x, y, w, h)
        coldata = point_node.pixelData(x, y, w, h)
        
        #procces data
        data = fill(coldata, linedata, w,h, self.opacity_threshold.value())
        ex = self.expansion.value()
        if ex>0: data = extra_expand(data, w,h, ex)

        #copy to Color
        color_node.setPixelData(data, x, y, w, h)
        
        if active_node!=None:
            doc.setActiveNode(active_node)
        #refresh
        doc.refreshProjection()

    def fill_animation(self):
        doc = Krita.instance().activeDocument()
        if doc is None:
            return
        
        active_node = doc.activeNode()

        r = self.getLayers(doc)
        if r==None:
            return
        line_node,point_node,color_node,x,y,w,h = r

        if not color_node.animated:
            raise RuntimeWarning("Output Layer is not animation enabled, delete it or create a new one")
        
        frame_start=int(self.anim_start.text())
        frame_end=int(self.anim_end.text())

        if frame_end<frame_start:
            frame_end=frame_start

        for frame in range(frame_start,frame_end+1):
            if color_node.hasKeyframeAtTime(frame):
                doc.setCurrentTime(frame)
                #get pixel data
                linedata = line_node.pixelData(x, y, w, h)
                coldata = point_node.pixelData(x, y, w, h)
                
                #procces data
                data = fill(coldata, linedata, w,h, self.opacity_threshold.value())
                ex = self.expansion.value()
                if ex>0: data = extra_expand(data, w,h, ex)

                #copy to Color
                color_node.setPixelData(data, x, y, w, h)
        
        if active_node!=None:
            doc.setActiveNode(active_node)
        #refresh
        doc.refreshProjection()

    def getLayers(self, doc):
        #get Layers
        ltext = self.line_input.text()
        ptext = self.color_point_input.text()
        ctext = self.color_output_input.text()
        cpytext = self.copy_input.text()
        line_node = doc.nodeByName(ltext)
        point_node = doc.nodeByName(ptext)
        color_node = doc.nodeByName(ctext)
        copynode = doc.nodeByName(cpytext)

        #if theres no input Layers create them and return
        if not all([line_node,point_node]):
            if line_node is None:
                line_node = doc.createNode(ltext, "paintLayer")
                doc.rootNode().addChildNode(line_node, None)
            if point_node is None:
                point_node = doc.createNode(ptext, "paintLayer")
                doc.rootNode().addChildNode(point_node, None)
            return None
        
        #create output layer
        if color_node is None:
            if copynode is None:
                color_node = point_node.duplicate()
            else:
                color_node = copynode.duplicate()
            color_node.setName(ctext)
            doc.rootNode().addChildNode(color_node, None)

        #get bounds
        bounds = doc.bounds()
        x, y, w, h = bounds.x(), bounds.y(), bounds.width(), bounds.height()

        return line_node,point_node,color_node,x,y,w,h

    def canvasChanged(self, canvas):
        pass
