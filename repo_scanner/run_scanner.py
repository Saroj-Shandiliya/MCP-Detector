import sys
import os

# Robustly add 'src' to path relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    # Insert at beginning to override any installed versions
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    try:
        from repo_scanner.cli.main import cli
        cli()
    except ImportError as e:
        print(f"Error launching scanner: {e}")
        print("Ensure you are running this script from the 'repo_scanner' directory.")
        sys.exit(1)
