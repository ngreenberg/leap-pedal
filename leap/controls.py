import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

import subprocess

class SampleListener(Leap.Listener):
    volume = 0

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()
        prev_frame = controller.frame(1)

        if len(frame.hands) > 0 and len(prev_frame.hands) != 0:
            hand = frame.hands[0]
            prev_hand = prev_frame.hands[0]
            self.volume += (hand.palm_position[1] - prev_hand.palm_position[1]) * 1
            self.volume = max(0, self.volume)
            self.volume = min(100, self.volume)
            print self.volume
            volume_string = str(self.volume) + "%"

            FNULL = open(os.devnull, 'w')
            subprocess.call(["amixer", "-D", "pulse", "sset", "Master", volume_string], stdout=FNULL, stderr=subprocess.STDOUT)

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()
