#!/usr/bin/env python3
# harness.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layer_10.cli import main

if __name__ == "__main__":
    main()