import sys
import os

# Ensure the project root is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.main import cli

if __name__ == '__main__':
    cli()
