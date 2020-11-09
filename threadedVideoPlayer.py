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


class ExtractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')    # Open the video clip
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))     # Total number of frames
        self.count = 0  # Initialize number of frame counter

    def run(self):
        global frames_queue
        # read one frame
        success, image = self.videoCapture.read()

        while True:
            if success and len(frames_queue.queue) <= frames_queue.queueCapacity:
                frames_queue.append_frame(image)  # Append frame to the queue
                success, image = self.videoCapture.read()    # Read another frame
                print(f'Reading frame {self.count}')
                self.count += 1     # Increment the counter

            if self.count == self.totalFrames:  # If counter reaches the total number of frames, break
                frames_queue.append_frame(-1)
                break
        return


if __name__ == '__main__':
    frames_queue = Queue(9)
