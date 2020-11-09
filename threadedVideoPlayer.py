#! /usr/bin/env python3
from threading import Thread, Semaphore, Lock
import cv2, time


class Queue:
    def __init__(self, capacity):
        self.queue = []
        self.full_count = Semaphore(0)
        self.empty_count = Semaphore(24)    # 24fps
        self.lock = Lock()
        self.queueCapacity = capacity   # Queues must be bounded at ten frames

    def append_frame(self, frame):  # Append frame to the queue
        self.empty_count.acquire()
        self.lock.acquire()     # Lock thread
        self.queue.append(frame)    # Append frame
        self.lock.release()     # Release thread
        self.full_count.release()
        return

    def pop_frame(self):    # Pop frame from the queue
        self.full_count.acquire()
        self.lock.acquire()     # Lock thread
        frame = self.queue.pop(0)   # Pop frame
        self.lock.release()     # Release thread
        self.empty_count.release()
        return frame


class FramesExtractor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.video_capture = cv2.VideoCapture('clip.mp4')    # Open the video clip
        self.total_frames = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))     # Total number of frames
        self.count = 0  # Initialize number of frame counter

    def run(self):
        global frames_queue
        # read one frame
        success, image = self.video_capture.read()

        while True:
            if success and len(frames_queue.queue) <= frames_queue.queueCapacity:
                frames_queue.append_frame(image)  # Append frame to the queue
                success, image = self.video_capture.read()    # Read another frame
                print(f'Reading frame {self.count}')
                self.count += 1     # Increment the counter

            if self.count == self.total_frames:  # If counter reaches the total number of frames, break
                frames_queue.append_frame(-1)
                break
        return


class GrayScaleConvertor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.count = 0  # initialize frame count

    def run(self):
        global frames_queue
        global grayscale_queue
        while True:
            if frames_queue.queue and len(grayscale_queue.queue) <= grayscale_queue.queueCapacity:
                frame = frames_queue.pop_frame()    # Get frame from the queue

                if type(frame) == int and frame == -1:
                    grayscale_queue.append_frame(-1)
                    break
                print(f'Converting Frame {self.count}')
                grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)    # Convert the image to grayscale
                grayscale_queue.append_frame(grayscale_frame)   # Append grayscale frame to the grayscale queue
                self.count += 1     # Increment frame counter
        return


if __name__ == '__main__':
    frames_queue = Queue(9)
    grayscale_queue = Queue(9)
    extract_frames = FramesExtractor()
    extract_frames.start()
    convert_to_grayscale = GrayScaleConvertor()
    convert_to_grayscale.start()

