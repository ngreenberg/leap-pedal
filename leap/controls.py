import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

import subprocess

class SampleListener(Leap.Listener):
    volume = 0

    gesture = None
    start_time = None

    is_swiping = False
    last_swipe_time = 0

    def on_connect(self, controller):
        print "Connected"

    def on_frame(self, controller):
        frame = controller.frame()
        prev_frame = controller.frame(1)

        if len(frame.hands) > 0:
            hand = frame.hands[0]

            # volume_string = str((1-hand.pinch_strength)*100) + "%"
            # FNULL = open(os.devnull, 'w')
            # subprocess.call(["amixer", "-D", "pulse", "sset", "Master", volume_string], stdout=FNULL, stderr=subprocess.STDOUT)

            normal = hand.palm_normal
            direction = hand.direction

            pitch = direction.pitch * Leap.RAD_TO_DEG
            roll = normal.roll * Leap.RAD_TO_DEG
            yaw = direction.yaw * Leap.RAD_TO_DEG

            # for finger in hand.fingers.extended():
            #     print finger.type,
            # print ""

            if len(prev_frame.hands) != 0:
                prev_hand = prev_frame.hands[0]

                extended_fingers = hand.fingers.extended()

                # if len(prev_hand.fingers.extended()) == 0:
                #     self.start_time = frame.timestamp

                #     if len(extended_fingers) == 1:
                #         if extended_fingers[0].type == 0:
                
                if len(extended_fingers) == 1 and extended_fingers[0].type == 0:
                    if len(prev_hand.fingers.extended()) == 0:
                        self.start_time = frame.timestamp

                if len(extended_fingers) > 1 and self.start_time is not None:
                    self.start_time = None

                if len(extended_fingers) == 0 and self.start_time is not None:
                    length = frame.timestamp - self.start_time
                    length /= 1000000.
                    print "gap:", length
                    self.start_time = None

                if hand.grab_strength == 1 and len(hand.fingers.extended()) == 0:
                    return

                if len(extended_fingers) == 5 and len(prev_hand.fingers.extended()) == 5:
                    if roll < 25 and roll > -25:
                        self.volume += (hand.palm_position[1] - prev_hand.palm_position[1]) * 1
                        self.volume = max(0, self.volume)
                        self.volume = min(100, self.volume)
                        print "volume:", self.volume
                        volume_string = str(self.volume) + "%"

                        FNULL = open(os.devnull, 'w')
                        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", volume_string], stdout=FNULL, stderr=subprocess.STDOUT)
                    else:
                        if hand.palm_velocity[0] < 150 and hand.palm_velocity[0] > -150:
                            if self.is_swiping:
                                self.is_swiping = False
                        else:
                            if not self.is_swiping:
                                if frame.timestamp - self.last_swipe_time > 750000:
                                    self.is_swiping = True
                                    self.last_swipe_time = frame.timestamp
                                    if hand.palm_velocity[0] > 0:
                                        print "pitch: +1"
                                    else:
                                        print "pitch: -1"

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
