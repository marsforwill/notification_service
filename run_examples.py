#!/usr/bin/env python3
"""
Main entry point for the notification service demonstration
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from examples.usage_examples import main

if __name__ == "__main__":
    main()
