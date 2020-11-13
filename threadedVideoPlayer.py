#! /usr/bin/env python3
from threading import Thread, Semaphore, Lock
import cv2


class Queue:
    def __init__(self, capacity):
        self.queue = []
        self.semaphore = Semaphore(capacity)
        self.lock = Lock()
        self.queueCapacity = capacity   # Queues must be bounded at ten frames

    def append_frame(self, frame):  # Append frame to the queue
        self.lock.acquire()
        self.semaphore.acquire()
        self.queue.append(frame)    # Append frame
        self.semaphore.release()
        self.lock.release()
        return

    def pop_frame(self):    # Pop frame from the queue
        self.lock.acquire()
        self.semaphore.acquire()
        frame = self.queue.pop(0)   # Pop frame
        self.semaphore.release()
        self.lock.release()
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
            # Queues must be bounded at ten frames
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
            # Queues must be bounded at ten frames
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


class Display(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42     # The answer to everything
        self.count = 0      # Initialize frame count

    def run(self):
        global grayscale_queue
        while True:
            if grayscale_queue.queue:
                frame = grayscale_queue.pop_frame()     # Get frame from the grayscale queue

                if type(frame) == int and frame == -1:
                    break
                print(f'Displaying Frame{self.count}')
                # Display the frame in a window called "Video"
                cv2.imshow('bIg_CHuNGuz.mp(math.sqrt(16))', frame)
                # Get the next frame filename
                self.count += 1
                # Wait for 42 ms and check if the user wants to quit
                if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                    break
        # Make sure we cleanup the windows, otherwise we might end up with a mess
        cv2.destroyAllWindows()
        return


if __name__ == '__main__':
    frames_queue = Queue(10)
    grayscale_queue = Queue(10)
    extract_frames = FramesExtractor()
    extract_frames.start()
    convert_to_grayscale = GrayScaleConvertor()
    convert_to_grayscale.start()
    display_frames = Display()
    display_frames.start()

