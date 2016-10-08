import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
import pyaudio
from audio import audioProcessor

def main():
    volume = 0

    gesture = None
    start_time = None

    is_swiping = False
    last_swipe_time = 0

    WIDTH = 2
    CHANNELS = 2
    RATE = 44100
    p = pyaudio.PyAudio()

    controller = Leap.Controller()
    ap = audioProcessor()
    stream = p.open(format=p.get_format_from_width(WIDTH),
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    stream_callback=ap.callback)

    stream.start_stream()
    while stream.is_active():
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
                #     start_time = frame.timestamp

                #     if len(extended_fingers) == 1:
                #         if extended_fingers[0].type == 0:

                if len(extended_fingers) == 1 and extended_fingers[0].type == 0:
                    if len(prev_hand.fingers.extended()) == 0:
                        start_time = frame.timestamp

                if len(extended_fingers) > 1 and start_time is not None:
                    start_time = None

                if len(extended_fingers) == 0 and start_time is not None:
                    length = frame.timestamp - start_time
                    length /= 1000000.
                    print "gap:", length
                    start_time = None

                if hand.grab_strength == 1 and len(hand.fingers.extended()) == 0:
                    return

                if len(extended_fingers) == 5 and len(prev_hand.fingers.extended()) == 5:
                    if roll < 25 and roll > -25:
                        volume += (hand.palm_position[1] - prev_hand.palm_position[1]) * 1
                        volume = max(0, volume)
                        volume = min(100, volume)
                        print "volume:", volume
                        volume_string = str(volume) + "%"

                        FNULL = open(os.devnull, 'w')
                        subprocess.call(["amixer", "-D", "pulse", "sset", "Master", volume_string], stdout=FNULL, stderr=subprocess.STDOUT)
                    else:
                        if hand.palm_velocity[0] < 150 and hand.palm_velocity[0] > -150:
                            if is_swiping:
                                is_swiping = False
                        else:
                            if not is_swiping:
                                if frame.timestamp - last_swipe_time > 750000:
                                    is_swiping = True
                                    last_swipe_time = frame.timestamp
                                    if hand.palm_velocity[0] > 0:
                                        print "pitch: +1"
                                    else:
                                        print "pitch: -1"
        # time.sleep(0.1)


    stream.stop_stream()
    stream.close()

    p.terminate()
    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
