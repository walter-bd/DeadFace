import argparse
import math
import time

from vmc_sender import VmcBlendshapeSender


def main():
    parser = argparse.ArgumentParser(
        description="Send test VMC blendshape messages to VSeeFace."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=39540)
    parser.add_argument("--frames", type=int, default=180)
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    sender = VmcBlendshapeSender(
        host=args.host,
        port=args.port,
        debug=args.debug,
    )

    blendshape_order = [
        "jawOpen",
        "eyeBlinkLeft",
        "eyeBlinkRight",
        "mouthSmileLeft",
        "mouthSmileRight",
    ]

    print(f"[VMC-TEST] Sending to {args.host}:{args.port}")
    print("[VMC-TEST] Press Ctrl+C to stop.")

    frame_delay = 1.0 / max(args.fps, 1.0)

    try:
        for frame_index in range(args.frames):
            phase = frame_index / 10.0
            values = {
                "jawOpen": (math.sin(phase) + 1.0) * 0.5,
                "eyeBlinkLeft": (math.sin(phase * 1.7) + 1.0) * 0.5,
                "eyeBlinkRight": (math.cos(phase * 1.7) + 1.0) * 0.5,
                "mouthSmileLeft": (math.sin(phase * 0.8) + 1.0) * 0.5,
                "mouthSmileRight": (math.cos(phase * 0.8) + 1.0) * 0.5,
            }
            sender.send_blendshapes(values, blendshape_order)
            time.sleep(frame_delay)
    except KeyboardInterrupt:
        pass

    print("[VMC-TEST] Done.")


if __name__ == "__main__":
    main()
