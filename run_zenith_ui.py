#!/usr/bin/env python3
"""
Quick launcher for ZENITH UI
Run this script to start the ZENITH voice assistant with GUI
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from zenith_ui import main
    print("=" * 60)
    print("🤖 ZENITH - Voice Assistant UI")
    print("=" * 60)
    print("\nStarting ZENITH GUI...")
    main()
except ImportError as e:
    print(f"Error: Missing required module: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
