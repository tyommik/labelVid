#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import os
import codecs
from libs.constants import DEFAULT_ENCODING
from collections import namedtuple

CACHE_EXT = '.log'
ENCODE_METHOD = DEFAULT_ENCODING

Detection = namedtuple('Detection', 'pos, x1, y1, x2, y2, obj_class, precision')

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
                        pos, x1, y1, x2, y2, obj_class, precision = line.split(' ')
                        detection = Detection(int(float(pos)), int(x1), int(y1), int(x2), int(y2), int(obj_class),
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
                            out.write(f'{detection.pos} {detection.x1} {detection.y1} {detection.x2} {detection.y2} {detection.obj_class} 0\n')
                    out.write("# end")
            except Exception as err:
                print(f'{type(err).__name__, str(err)}')



    def save(self, filepath):
        self.saveYoloFormat(filepath)

    def __getitem__(self, item):
        detections = self.detections.get(item)
        # FIXME фигня с координатами, перепутаны
        shapes = [self.addShape(self.classes[int(det.obj_class)], det.x1, det.y1, det.x2, det.y2, 0.5) for det in detections] if detections else []
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

