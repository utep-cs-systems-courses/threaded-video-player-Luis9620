#! /usr/bin/env python3
from threading import Thread, Semaphore, Lock
import cv2, time


class Queue:
    def __init__(self,capacity):
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


