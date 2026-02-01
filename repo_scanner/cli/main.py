import os
import json
import click
from rich.console import Console
from rich.table import Table
from repo_scanner.scanner import (
    GitHubClient, RepoFetcher, FileFilter,
    KeywordScanner, DependencyScanner, ASTScanner,
    Classifier, setup_logger, load_config
)
from repo_scanner.scanner.result import ScanResult

logger = setup_logger()
console = Console()

@click.group()
@click.option('--config', default='config/scanner_config.yaml', help='Path to scanner config.')
@click.option('--languages', default='config/languages.yaml', help='Path to languages config.')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub API Token.')
@click.pass_context
def cli(ctx, config, languages, token):
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
        logger.error(f"Failed to scan {repo_full_name}: {e}")
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
    if fmt == 'json':
        print(result.json(indent=2))
    else:
        table = Table(title=f"Scan Result: {result.repository}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Classification", result.classification)
        table.add_row("Confidence", f"{result.confidence:.2f}")
        table.add_row("Files Scanned", str(result.files_scanned))
        table.add_row("Languages", ", ".join(result.languages_detected))
        
        console.print(table)
        
        if result.indicators:
            ind_table = Table(title="Indicators Found")
            ind_table.add_column("Type")
            ind_table.add_column("Value")
            ind_table.add_column("File")
            
            for ind in result.indicators[:10]: # Limit to top 10
                ind_table.add_row(ind.type, ind.value, os.path.basename(ind.file) if ind.file else "")
            
            console.print(ind_table)

if __name__ == '__main__':
    cli()
