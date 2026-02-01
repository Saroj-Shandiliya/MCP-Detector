# GitHub Repository Code Scanner & MCP Detector

A modular, extensible Python tool designed to scan GitHub repositories (or local directories) in order to detect Model Context Protocol (MCP) Server implementations, transports, and tools.

**Key Features:**
*   **MCP Support**: Pre-configured with a "Master Keyword Bank" to detect MCP Servers, Transports (SSE/Stdio), and Tools.
*   **Protocol Agnostic**: Logic is data-driven via `scanner_config.yaml`.
*   **Deep Scanning**: Combines Keyword matching (Regex), Dependency parsing, and AST analysis.
*   **Zero-Install**: Can be run via a simple launcher script without system-wide installation.

---

## � Quick Start (Recommended)

The most reliable way to run the scanner is using the included launcher script, which avoids common Python path/permission issues.

### 1. Navigate to the Scanner Directory
```bash
cd "d:\MCP Detector\MCP-Detector\repo_scanner"
```
*(Or wherever you downloaded this project -> go into the `repo_scanner` folder)*

### 2. Run a Scan
Use `python run_scanner.py` followed by the command you want.

**Scan a GitHub Repository:**
```bash
python run_scanner.py repo owner/name
```
*Example:*
```bash
python run_scanner.py repo modelcontextprotocol/python-sdk
```

**Scan a Local Directory:**
```bash
python run_scanner.py local "../dummy_repo"
```

**Scan a User or Organization:**
```bash
# Scan a specific user
python run_scanner.py user some-username

# Scan an organization
python run_scanner.py org modelcontextprotocol
```

---

## ⚙️ Options

| Flag | Description | Default |
|------|-------------|---------|
| `--output` | Output format: `table` (default) or `json`. | `table` |
| `--token` | GitHub PAT (Personal Access Token) for higher API rate limits. | `None` (or env `GITHUB_TOKEN`) |
| `--config` | Custom path to a config YAML file. | Auto-detected |

**Example with JSON output:**
```bash
python run_scanner.py repo facebook/react --output json
```

---

## 🔧 Configuration

The detection logic is defined in:
`src/repo_scanner/config/scanner_config.yaml`

It includes:
*   **Server Indicators**: +5.0 score (e.g., `@modelcontextprotocol/sdk` dependency).
*   **Transports**: +4.0 score (e.g., `SSEServerTransport`, `StdioServerTransport`).
*   **RPC Methods**: +3.0 score (e.g., `listTools`, `callTool`).

**Scoring Thresholds:**
*   **>= 8.0**: `SERVER` (Confirmed Implementation)
*   **5.0 - 7.9**: `PROTOCOL_RELATED` (Likely uses the protocol)
*   **< 5.0**: `UNKNOWN` or `CLIENT`

---

## 📦 Alternative Installation

If you prefer to install it as a command-line tool (requires Admin/Permission):

```bash
cd repo_scanner
pip install -e .
```

Then you can use the `repo-scanner` command directly:
```bash
repo-scanner repo owner/name
```
*If this fails with "Command not found", please stick to the `run_scanner.py` method above.*
