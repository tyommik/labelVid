import cv2
import numpy as np
from libs.ffmpeg_reader import FFMPEG_VideoReader

def mat2bytes(image):
    image = image[:, :, ::-1]
    return cv2.imencode('.jpg', image)[1].tostring()


# class VideoCapture0:
#     def __init__(self, video_source, start_frame=0, shift_time=0):
#         self.video = cv2.VideoCapture(video_source)
#         self.start_frame = start_frame
#         self.shift = shift_time
#
#         if not self.video.isOpened():
#             raise ValueError("Unable to open video source", video_source)
#
#         self.width = int(self.video.get(3))  # int
#         self.height = int(self.video.get(4)) # int
#
#         self.set_position(self.start_frame)
#         self.ps_frame = None
#
#     def set_position(self, position=0):
#         if position:
#             self.video.set(1, position)
#         else:
#             self.video.set(1, self.start_frame - 1)
#
#     def get_position(self):
#         return self.video.get(1)
#
#     def get_frame(self):
#         if self.video.isOpened():
#             ret, frame = self.video.read()
#
#             if ret:
#                 return mat2bytes(frame)
#             else:
#                 return None
#
#     def get_time(self):
#         f = self.get_position() + self.shift
#         hours = int(f // 90000)
#         minutes = int((f - hours * 90000) // 1500)
#         secondes = int((f - hours * 90000 - minutes * 1500) // 25)
#         return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, secondes)
#
#
#     def length(self):
#         if self.video.isOpened():
#             return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))


class VideoCapture:
    def __init__(self, video_source, start_frame=0, shift_time=0):
        self.video = FFMPEG_VideoReader(video_source, True)
        self.video.initialize(starttime=0)
        self.duration = self.video.ffmpeg_duration * 1000
        self.start_frame = start_frame
        self.shift = shift_time
        self.pos = start_frame

        self.set_position(self.start_frame)
        self.cached_frame = None

    def set_position(self, position=0):
        self.pos = position
        self.video.skip_frames(position)

    def get_position(self):
        return self.video.pos

    def get_frame(self, pos):
        if pos == self.pos and self.cached_frame is not None:
            return self.cached_frame
        self.pos = pos
        try:
            frame = self.video.get_frame(t=pos)
        except OSError as err:
            print('Bad frame!')
        else:
            frame = mat2bytes(frame)
            self.cached_frame = frame
            return frame

    def get_time(self):
        pos = self.video.pos
        fps = self.video.fps
        hours = int(pos // 3600 // fps)
        minutes = int((pos - (hours * 3600 * fps)) // (60 * fps))
        secondes = int((pos - (hours * 3600 * fps) - minutes * (60 * fps)) // fps)
        return (secondes + minutes * 60 + hours * 3600) * 1000
        # return "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, secondes)

    def length(self):
        return self.video.nframes
