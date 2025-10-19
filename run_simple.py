#!/usr/bin/env python3
"""
Simple CLI runner for VideoLib - launches the interactive interface
"""
import sys
import os
from pathlib import Path

def main():
    """Main entry point - launches interactive CLI"""
    # Add current directory to Python path for importing
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(current_dir.parent))
    
    try:
        # Import and run the interactive CLI
        from cli.interactive_main import main as interactive_main
        interactive_main()
    except ImportError as e:
        print(f"❌ Failed to import interactive CLI: {e}")
        print("Make sure all required files are present:")
        print("- cli/interactive_main.py")
        print("- videolib/ package")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
