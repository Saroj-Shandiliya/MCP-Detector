# GitHub Repository Code Scanner & MCP Detector

A modular, extensible, and scalable Python tool designed to scan GitHub repositories (or local directories) to identify and classify protocol-based server implementations.

**Key Features:**
*   **MCP Support**: Pre-configured with a "Master Keyword Bank" to detect Model Context Protocol (MCP) Servers, Transports, and Tools.
*   **Protocol Agnostic**: Logic is data-driven via `scanner_config.yaml`, allowing easy extension to other protocols (HTTP, gRPC, etc.).
*   **Multi-Scanner Architecture**: combines Keyword matching (Regex), Dependency parsing, and AST analysis for high-confidence scoring.
*   **Flexible Inputs**: Scan single repos, entire user profiles, or local folders.

---

## 📦 Installation

To use the tool, you must properly install the package. We recommend installing in "editable" mode so changes to config files take effect immediately.

```bash
# 1. Clone or Navigate to the project root
cd "path/to/MCP-Detector"

# 2. Install dependencies and the CLI tool
pip install -e repo_scanner
```

This registers the `repo-scanner` command in your system/environment.

---

## 🚀 Usage Guide

### 1. Scan a Remote GitHub Repository
Automatically downloads the repo to a temporary folder, scans it, and cleans up.

**Command:**
```bash
repo-scanner repo <owner>/<repository_name>
```

**Example:**
```bash
repo-scanner repo modelcontextprotocol/python-sdk
```
*Output: classification (SERVER/CLIENT) and key indicators found.*

### 2. Scan a Local Directory
Useful for private code or development folders.

**Command:**
```bash
repo-scanner local "<path_to_folder>"
```

**Example:**
```bash
repo-scanner local "D:\Projects\my-mcp-server"
```

### 3. Scan a GitHub User or Organization
Scans all public repositories belonging to a user or organization.

**User Scan:**
```bash
repo-scanner user <username>
```

**Organization Scan:**
```bash
repo-scanner org <organization_name>
```

---

## ⚙️ Options & Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--output` | Output format: `table` (default) or `json`. | `table` |
| `--token` | GitHub PAT (Personal Access Token) for higher API rate limits. | `None` (or env `GITHUB_TOKEN`) |
| `--config` | Custom path to a config YAML file. | `repo_scanner/config/scanner_config.yaml` |

**Example using JSON output:**
```bash
repo-scanner repo facebook/react --output json
```

---

## 🔧 Configuration

The scanner's brain is located in `repo_scanner/config/scanner_config.yaml`.

### Master Keyword Bank
We have pre-loaded this file with **MCP** detection rules:
*   **Dependencies**: matches `@modelcontextprotocol/sdk`, `mcp-server`, `flask`...
*   **Transports**: matches `SSEServerTransport`, `StdioServerTransport`.
*   **Methods**: matches `listTools`, `callTool`.

### Customizing
You can add your own patterns in `scanner_config.yaml`:
```yaml
patterns:
  - name: "My Custom Protocol"
    regex: '(?i)my-protocol-server'
    score: 5.0
    classification: "SERVER"
```

---

## 📊 Classification Logic

The system assigns a **Score** based on findings:
*   **>= 8.0**: Classified as `SERVER` (Confirmed Implementation).
*   **5.0 - 7.9**: Classified as `PROTOCOL_RELATED` (Likely uses the protocol).
*   **< 5.0**: `UNKNOWN` or `CLIENT` (if client score dominates).

**Scoring Weights:**
*   **Dependency Match**: +5.0 points (High confidence)
*   **Transport Class**: +4.0 points
*   **Method Definition**: +3.0 points
*   **Standard Keyword**: +0.1 points

---

## 🧪 Verification
To verify your installation and setup:

```bash
python tests/verify.py
```
This script runs a quick import check and scans a dummy string to ensure the configuration is loaded correctly.
