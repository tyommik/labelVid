#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
import codecs
from libs.constants import DEFAULT_ENCODING
from collections import namedtuple

TXT_EXT = '.txt'
ENCODE_METHOD = DEFAULT_ENCODING

# FIXME Тут похоже перепутан w, h  с x2, y2
Detection = namedtuple('Detection', 'pos, x, y, w, h, obj_class, precision')

class YOLOWriter:

    def __init__(self, foldername, filename, imgSize, databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.localImgPath = localImgPath
        self.verified = False

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)

    def BndBox2YoloLine(self, box, classList=[]):
        xmin = box['xmin']
        xmax = box['xmax']
        ymin = box['ymin']
        ymax = box['ymax']

        xcen = float((xmin + xmax)) / 2 / self.imgSize[1]
        ycen = float((ymin + ymax)) / 2 / self.imgSize[0]

        w = float((xmax - xmin)) / self.imgSize[1]
        h = float((ymax - ymin)) / self.imgSize[0]

        # PR387
        boxName = box['name']
        if boxName not in classList:
            classList.append(boxName)

        classIndex = classList.index(boxName)

        return classIndex, xcen, ycen, w, h

    def save(self, classList=[], targetFile=None):

        out_file = None #Update yolo .txt
        out_class_file = None   #Update class list .txt

        if targetFile is None:
            out_file = open(
            self.filename + TXT_EXT, 'w', encoding=ENCODE_METHOD)
            classesFile = os.path.join(os.path.dirname(os.path.abspath(self.filename)), "classes.txt")
            out_class_file = open(classesFile, 'w')

        else:
            out_file = codecs.open(targetFile, 'w', encoding=ENCODE_METHOD)
            classesFile = os.path.join(os.path.dirname(os.path.abspath(targetFile)), "classes.txt")
            out_class_file = open(classesFile, 'w')


        for box in self.boxlist:
            classIndex, xcen, ycen, w, h = self.BndBox2YoloLine(box, classList)
            # print (classIndex, xcen, ycen, w, h)
            out_file.write("%d %.6f %.6f %.6f %.6f\n" % (classIndex, xcen, ycen, w, h))

        # print (classList)
        # print (out_class_file)
        for c in classList:
            out_class_file.write(c+'\n')

        out_class_file.close()
        out_file.close()



class YoloCacheReader:

    def __init__(self, filepath=None, classListPath=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.detections = {}
        self.filepath = filepath
        self.classListPath = os.path.abspath(classListPath)

        if filepath:
            dir_path = os.path.dirname(os.path.realpath(self.filepath))
            extClassListPath = os.path.join(dir_path, "classes.txt")

            if os.path.exists(extClassListPath):
                self.classListPath = extClassListPath

        with open (self.classListPath, 'r') as classesFile:
            self.classes = [cl.strip('\n') for cl in classesFile.readlines() if cl.strip('\n')]

        if not self.classes:
            raise ValueError ('No classes in ', self.classListPath)
        # print (self.classes)


        self.verified = False
        if filepath:
            self.parseYoloFormat()


    def getShapes(self):
        return self.detections

    def addShape(self, label, xmin, ymin, xmax, ymax, difficult):
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        shape = (label, points, None, None, difficult)
        return shape

    def getDetection(self, pos, label, points, score):
        #FIXME сверить порядок с кэшем
        obj_class = self.classes.index(label) if label in self.classes else 0
        xs = [int(x[0]) for x in points]
        ys = [int(y[1]) for y in points]
        xmin = min(xs)
        xmax = max(xs)
        ymin = min(ys)
        ymax = max(ys)

        detection = Detection(pos, xmin, ymin, xmax, ymax, obj_class, 0.0)
        return detection

    def parseYoloFormat(self):
        detections = {}
        def read_file():
            with open(self.filepath) as inf:
                for line in iter(inf):
                    if not line.startswith(('#')):
                        line = line.strip()
                        pos, x, y, w, h, obj_class, precision = line.split(' ')
                        detection = Detection(int(pos), int(x), int(y), int(w), int(h), int(obj_class),
                                              float(precision))
                        yield detection
        for detection in read_file():
            detections.setdefault(detection.pos, []).append(detection)
        self.detections = detections

    def saveYoloFormat(self, filepath):
        if self.detections:
            frames = sorted([frame for frame in self.detections.keys()])
            try:
                with open(filepath, 'w') as out:
                    out.write("# start\n")
                    for frame in frames:
                        detections = self.detections.get(frame, [])
                        for detection in detections:
                            out.write(f'{detection.pos} {detection.x} {detection.y} {detection.w} {detection.h} {detection.obj_class} 0\n')
                    out.write("# end")
            except Exception as err:
                print(f'{type(err).__name__, str(err)}')



    def save(self, filepath):
        self.saveYoloFormat(filepath)

    def __getitem__(self, item):
        detections = self.detections.get(item)
        # FIXME фигня с координатами, перепутаны
        shapes = [self.addShape(self.classes[int(det.obj_class)], det.x, det.y, det.w, det.h, 0.5) for det in detections] if detections else []
        return shapes

    def __setitem__(self, pos, value):
        if isinstance(value, list):
            detections = []
            for v in value:
                label = v['label']
                points = v['points']
                score = v['difficult']
                detection = self.getDetection(pos, label, points, score)
                detections.append(detection)
            self.detections[pos] = detections
        else:
            label = value['label']
            points = value['points']
            score = value['difficult']
            detection = self.getDetection(pos, label, points, score)
            self.detections[pos] = [detection]

