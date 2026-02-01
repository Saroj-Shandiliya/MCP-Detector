import sys
import os
import traceback
from rich.console import Console
from rich.panel import Panel

# Simple verification script to check if the scanner is wired up correctly
# Requires 'repo_scanner' to be installed (pip install -e .)

console = Console()

def run_verify():
    try:
        console.print("[bold blue]Verifying Scanner Imports...[/bold blue]")
        from repo_scanner.scanner import (
            KeywordScanner, DependencyScanner, Classifier, ScanResult, FileFilter, load_config
        )
        console.print("[green]✔ Imports successful[/green]")
        
        # Load Config
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "repo_scanner", "config", "scanner_config.yaml")
        
        console.print(f"[bold blue]Loading Config from {config_path}...[/bold blue]")
        config = load_config(config_path)
        
        if config and "patterns" in config:
            count = len(config["patterns"])
            console.print(f"[green]✔ Config loaded with {count} patterns[/green]")
        else:
            console.print("[red]✘ Config failed to load or is empty[/red]")
            return

        # Dummy Check
        # simulate content with MCP keywords
        content = "import SSEServerTransport\nfrom mcp import Server"
        path = "test_server.py"
        
        scanner = KeywordScanner(config)
        indicators = scanner.scan(path, content)
        
        console.print(f"[bold blue]Scanning dummy content...[/bold blue]")
        for ind in indicators:
            console.print(f" - Found: {ind.value} (Score: {ind.score})")
            
        if len(indicators) >= 2:
            console.print("[green]✔ Scanner detected keywords[/green]")
        else:
            console.print("[red]✘ Scanner matches too low[/red]")

    except ImportError:
        console.print(Panel("[red]ImportError: repo_scanner package not found.\nPlease run 'pip install -e .' in the repo_scanner directory.[/red]", title="Setup Required"))
    except Exception:
        console.print_exception()

if __name__ == "__main__":
    run_verify()
