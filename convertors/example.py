import json
from collections import namedtuple

INPUT = r'../demo/demo.log'
OUTPUT = r'../demo/demo.json'

Detection = namedtuple('Detection', 'pos, x1, y1, x2, y2, obj_class, precision')

class Event:
    def __init__(self, start):
        self.detections = []
        self.detections_map = {}
        self.__start = start
        self.__stop = None

    def __repr__(self):
        return "Event start={0} detection_length={1}".format(self.start, len(self.detections))

    def __hash__(self):
        return hash(self.start)

    @property
    def start(self):
        return self.__start

    @property
    def stop(self):
        return self.__stop or self.detections[-1].pos

    @property
    def length(self):
        return self.stop - self.start

    def to_dict(self):
        if self.detections:
            first = self.detections[0]
            return {
                "x": first.x1,
                "y": first.y1,
                "w": abs(first.x2 - first.x1),
                "h": abs(first.y2 - first.y1),
                "label": first.obj_class,
                "begin": self.start,
                "end": self.stop
            }


def read_file(file):
    with open(file, 'r') as inf:
        for line in iter(inf):
            if not line.startswith("#"):
                line = line.strip()
                pos, x1, y1, x2, y2, obj_class, precision = line.split(' ')
                detection = Detection(int(pos), int(x1), int(y1), int(x2), int(y2), int(obj_class), float(precision))
                yield detection


def collect_events():
    events = []
    step = None
    for detection in read_file(INPUT):
        if step is None:
            step = detection.pos
            event = Event(detection.pos)
            event.detections.append(detection)
            continue

        # if between events 5 or more frames
        if detection.pos - step <= 5:
            event.detections.append(detection)
        else:
            events.append(event)
            event = Event(detection.pos)
            event.detections.append(detection)

        step = detection.pos

    for event in events:
        for det in event.detections:
            event.detections_map.setdefault(det.pos, []).append(det)
    return events

if __name__ == '__main__':

    events = collect_events()
    events = [event.to_dict() for event in events]
    json_data = json.dumps(events)
    with open(OUTPUT, 'w') as ouf:
        ouf.write(json_data)