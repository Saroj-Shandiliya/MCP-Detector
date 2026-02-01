import logging
import sys
import os
import click
from rich.console import Console
from rich.table import Table
from ..scanner.utils import setup_logger, load_config
from ..scanner.github_client import GitHubClient
from ..scanner.repo_fetcher import RepoFetcher
from ..scanner.file_filter import FileFilter
from ..scanner.scanners.keyword_scanner import KeywordScanner
from ..scanner.scanners.dependency_scanner import DependencyScanner
from ..scanner.scanners.ast_scanner import ASTScanner
from ..scanner.classifier import Classifier
from ..scanner.result import ScanResult

logger = setup_logger()
console = Console()

@click.group()
@click.pass_context
@click.option('--config', default=None, help='Path to scanner config.')
@click.option('--languages', default=None, help='Path to languages config.')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub API Token.')
def cli(ctx, config, languages, token):
    # Resolve default paths relative to package if not provided
    if not config:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config = os.path.join(base_dir, "config", "scanner_config.yaml")
        if not os.path.exists(config):
            # Fallback to local config dir if running from source root without install
            config = "config/scanner_config.yaml"
            
    if not languages:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        languages = os.path.join(base_dir, "config", "languages.yaml")
        if not os.path.exists(languages):
            languages = "config/languages.yaml"

    ctx.ensure_object(dict)
    ctx.obj['config'] = load_config(config)
    ctx.obj['languages'] = load_config(languages)
    ctx.obj['token'] = token
    
    # Initialize components
    ctx.obj['github_client'] = GitHubClient(token)
    ctx.obj['repo_fetcher'] = RepoFetcher(token)

@cli.command()
@click.argument('repo_name') # owner/repo
@click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format.')
@click.pass_context
def repo(ctx, repo_name, output):
    """Scan a specific repository (owner/name)."""
    scan_repo(ctx, repo_name, output)

@cli.command()
@click.argument('username')
@click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format.')
@click.pass_context
def user(ctx, username, output):
    """Scan all repositories for a user."""
    client = ctx.obj['github_client']
    for repo_meta in client.get_user_repos(username):
        scan_repo(ctx, repo_meta.full_name, output)

@cli.command()
@click.argument('org')
@click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format.')
@click.pass_context
def org(ctx, org, output):
    """Scan all repositories for an organization."""
    client = ctx.obj['github_client']
    for repo_meta in client.get_org_repos(org):
        scan_repo(ctx, repo_meta.full_name, output)

@cli.command()
@click.argument('path')
@click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format.')
@click.pass_context
def local(ctx, path, output):
    """Scan a local directory."""
    scan_local(ctx, path, output)

def scan_repo(ctx, repo_full_name, output_format):
    config = ctx.obj['config']
    langs = ctx.obj['languages']
    token = ctx.obj['token']
    
    client = ctx.obj['github_client']
    fetcher = ctx.obj['repo_fetcher']
    
    try:
        if "/" not in repo_full_name:
             logger.error(f"Invalid repo name: {repo_full_name}. Must be owner/repo.")
             return

        owner, name = repo_full_name.split("/")
        
        # 1. Get Metadata
        # metadata = client.get_repo_metadata(owner, name) # Optional optimization
        
        # 2. Download and Extract
        url = client.get_archive_url(owner, name)
        
        with fetcher.fetch_repo_zip(url) as repo_path:
            # 3. Initialize Scanners
            scanners = [
                KeywordScanner(config),
                DependencyScanner(),
                ASTScanner() 
            ]
            
            file_filter = FileFilter(langs.get('languages', {}))
            
            all_indicators = []
            files_scanned = 0
            file_extensions_seen = set()
            
            # 4. Scan Loop
            for file_data in file_filter.walk_repo(repo_path):
                files_scanned += 1
                file_extensions_seen.add(file_data.extension)
                
                for scanner in scanners:
                    indicators = scanner.scan(file_data.path, file_data.content)
                    all_indicators.extend(indicators)
            
            # 5. Classify
            classifier = Classifier(config)
            classification = classifier.classify(all_indicators)
            confidence = classifier.get_confidence(all_indicators)
            
            # 6. Result
            result = ScanResult(
                repository=repo_full_name,
                classification=classification,
                confidence=confidence,
                indicators=all_indicators,
                languages_detected=list(file_extensions_seen),
                files_scanned=files_scanned
            )
            
            output_result(result, output_format)

    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
             error_msg += " (Hint: Repo might be Private? Check token/typo.)"
        
        logger.error(f"Failed to scan {repo_full_name}: {error_msg}")
        # In a batch process, we might want to return an error result instead of just logging
        err_res = ScanResult(repository=repo_full_name, classification="ERROR")
        output_result(err_res, output_format)

def scan_local(ctx, path, output_format):
    config = ctx.obj['config']
    langs = ctx.obj['languages']
    
    if not os.path.exists(path):
        logger.error(f"Path not found: {path}")
        return

    try:
        # 1. Initialize Scanners
        scanners = [
            KeywordScanner(config),
            DependencyScanner(),
            ASTScanner() 
        ]
        
        file_filter = FileFilter(langs.get('languages', {}))
        
        all_indicators = []
        files_scanned = 0
        file_extensions_seen = set()
        
        # 2. Scan Loop
        for file_data in file_filter.walk_repo(path):
            files_scanned += 1
            file_extensions_seen.add(file_data.extension)
            
            for scanner in scanners:
                indicators = scanner.scan(file_data.path, file_data.content)
                all_indicators.extend(indicators)
        
        # 3. Classify
        classifier = Classifier(config)
        classification = classifier.classify(all_indicators)
        confidence = classifier.get_confidence(all_indicators)
        
        # 4. Result
        result = ScanResult(
            repository=path,
            classification=classification,
            confidence=confidence,
            indicators=all_indicators,
            languages_detected=list(file_extensions_seen),
            files_scanned=files_scanned
        )
        
        output_result(result, output_format)

    except Exception as e:
        logger.error(f"Failed to scan {path}: {e}")


def output_result(result: ScanResult, fmt: str):
    # 1. Save Full JSON to File
    try:
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        safe_name = result.repository.replace("/", "_").replace("\\", "_").replace(":", "")
        timestamp = result.timestamp.replace(":", "-").split(".")[0]
        filename = f"{results_dir}/{safe_name}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            f.write(result.model_dump_json(indent=2))
        
        console.print(f"[green]Full results saved to: {filename}[/green]")
        
    except Exception as e:
        logger.error(f"Failed to save results file: {e}")

    # 2. Print Summary to Console (Always, unless logic changes)
    # The user requested: "just show the confidence score and file name or path where the keywords matched"
    
    table = Table(title=f"Scan Result: {result.repository}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Classification", result.classification)
    table.add_row("Confidence", f"{result.confidence:.2f}")
    table.add_row("Files Scanned", str(result.files_scanned))
    table.add_row("Languages", ", ".join(result.languages_detected))
    
    console.print(table)
    
    if result.indicators:
        ind_table = Table(title="Indicators Found (Summary)")
        ind_table.add_column("Type", style="cyan")
        ind_table.add_column("Value", style="green")
        ind_table.add_column("File Path", style="yellow")
        
        # Sort by score/weight if possible, or just take top few
        # Showing full path might be long, so maybe relative or basename
        for ind in result.indicators[:15]: # Limit to top 15
            ind_table.add_row(
                ind.type, 
                ind.value, 
                ind.file if ind.file else "N/A"
            )
        
        console.print(ind_table)
        if len(result.indicators) > 15:
            console.print(f"... and {len(result.indicators) - 15} more indicators (see full JSON file).")

if __name__ == '__main__':
    cli()
