import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import repo_scanner
    print(f"Import repo_scanner OK: {repo_scanner.__file__}")
except Exception as e:
    print(f"Import repo_scanner FAILED: {e}")

try:
    import repo_scanner.scanner
    print(f"Import repo_scanner.scanner OK: {repo_scanner.scanner.__file__}")
except Exception as e:
    print(f"Import repo_scanner.scanner FAILED: {e}")

try:
    import repo_scanner.scanner.utils
    print(f"Import repo_scanner.scanner.utils OK")
except Exception as e:
    print(f"Import repo_scanner.scanner.utils FAILED: {e}")

try:
    import repo_scanner.cli
    print(f"Import repo_scanner.cli OK")
except Exception as e:
    print(f"Import repo_scanner.cli FAILED: {e}")
