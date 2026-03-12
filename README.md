# EthoClaw

[中文版本 (Chinese Version)](README-zh.md)

An open-source project in the field of Ethology built on top of OpenClaw.

## Why Develop EthoClaw

In behavioral analysis, EthoClaw can help researchers automate tedious processes such as preprocessing, data conversion, format matching, and environment configuration. It can also search for network information, generate analysis reports, result graphs, and interpret local literature, allowing researchers to focus more on solving scientific problems and improving research efficiency.

## Supported Features

- **Chart/Report Generation:**
  1. Generate speed heatmaps and trajectory heatmaps based on tracking data;
  2. Support violin plots, cluster plots, radar charts, etc. for multiple groups of data; automatically typeset experiment flow charts and analysis diagrams;
  3. Support CSV/Excel format conversion;
  4. Generate PDF analysis reports including experiment background, sample information, analysis content, and summaries.
- **Tutorial Assistance:**
  1. Provide detailed explanations for beginners on parameter calculation methods, chart data sources, clustering methods and parameters, etc., to facilitate writing the methods section of papers.
- **Local Knowledge Base:**
  1. Read local PDF papers and reports, summarize and output them, forming local research logs.
- **Network Search:**
  1. Obtain the latest papers through web or academic searches, supporting daily scheduled delivery of arxiv papers.
- **Note:**
  Since EthoClaw is built on OpenClaw, it inherits all of OpenClaw’s functionality, uses the same interface, and is fully compatible with all OpenClaw plugins.

## Planned Features

- Support target localization: Based on image recognition technology, automatically locate experimental targets (such as animals, environmental elements, etc.).
- Support pose estimation: Can access open-source pose estimation models/projects to automatically estimate the pose of experimental targets (such as head, back, tail, etc.).

## Quick Start

This project is built on OpenClaw, and its configuration and installation methods are similar to or the same as OpenClaw.

```bash
# Download and install nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
# Instead of restarting shell
\. "$HOME/.nvm/nvm.sh"
# Download and install Node.js:
nvm install 24
# Verify Node.js version:
node -v # Should print "v24.14.0".
# Download and install pnpm:
corepack enable pnpm
# Verify pnpm version:
pnpm -v

# Download EthoClaw code:
git clone https://github.com/penciler-star/EthoClaw.git
cd EthoClaw
# Install
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
# Configure EthoClaw environment
pnpm openclaw onboard --install-daemon
# Start EthoClaw
pnpm gateway:watch
```

## Project Effects
