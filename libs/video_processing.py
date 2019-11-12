import cv2
from libs.ffmpeg_reader import FFMPEG_VideoReader


def mat2bytes(image):
    image = image[:, :, ::-1]
    return cv2.imencode('.jpg', image)[1].tostring()


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

    def length(self):
        return self.video.nframes
