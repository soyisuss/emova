import time

class FPSSampler:

    def __init__(self, fps=3):

        self.interval = 1.0 / fps
        self.last_time = 0


    def should_process(self):

        now = time.time()

        if now - self.last_time >= self.interval:
            self.last_time = now
            return True

        return False