import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

import subprocess

class SampleListener(Leap.Listener):

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)

            volume = (hand.palm_position[1] - 50) / 4
            volume = max(0, volume)
            volume = min(100, volume)
            print volume
            volume_string = str(volume) + "%"

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
