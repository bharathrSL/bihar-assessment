"""Bounded retry policy for transient provider failures."""
import time
class Retry:
    def __init__(self, attempts: int=3, backoff: float=1.5): self.attempts, self.backoff=attempts, backoff
    def run(self, action):
        error=None
        for i in range(self.attempts):
            try: return action()
            except Exception as exc:
                error=exc
                if i+1 < self.attempts: time.sleep(self.backoff*(2**i))
        raise error
