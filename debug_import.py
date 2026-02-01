try:
    import repo_scanner.scanner.utils
    print("Success: modules found")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
