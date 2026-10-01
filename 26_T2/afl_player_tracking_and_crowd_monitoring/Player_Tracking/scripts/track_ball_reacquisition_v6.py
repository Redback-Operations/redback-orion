#!/usr/bin/env python3
"""Run the V5 motion tracker with controlled stale-track reacquisition enabled."""

from __future__ import annotations

import sys

from track_ball_motion_v5 import main


if __name__ == "__main__":
    if "--enable-controlled-reacquisition" not in sys.argv:
        sys.argv.insert(1, "--enable-controlled-reacquisition")
    main()
