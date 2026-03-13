# <p align="center">EthoClaw</p>

<p align="center">
  <img src="docs/EthoClaw.png" alt="EthoClaw" width="400"/>
</p>

[中文版本 (Chinese Version)](README-zh.md)

**EthoClaw** is an open-source project in the field of Ethology built on OpenClaw, with a core focus on implementing practical skills for behavioral research.
Targeting cumbersome workflows in ethological analysis—such as preprocessing, data conversion, format matching, and environment setup—EthoClaw not only automates these tasks for researchers but also supports web information retrieval, analytical report and result figure generation, local literature interpretation, automated object localization, and automatic pose estimation, enabling researchers to focus more on solving scientific questions and significantly improving research efficiency.

## Supported Species

- Black mouse

## Supported Experiment Scenarios

- Open field, elevated plus maze, and other 2D top-down shooting scenarios

## Supported Features

- **Automated Target Localization:**
  1. Based on image recognition technology, automatically locate experimental targets (such as animals, environmental elements, etc.).
- **Automatic Pose Estimation:**
  1. Access open-source pose estimation models/projects to automatically estimate the pose of experimental targets (such as head, back, tail, etc.).
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

## Quick Start

This project is built on OpenClaw, and its configuration and installation methods are similar to or the same as OpenClaw.

### System Requirements

- System requirements are the same as OpenClaw, recommend ubuntu 24.04 LTS version.
- If you want to enable automated pose estimation functionality, it is recommended to have an **NVIDIA GPU** with CUDA and cuDNN installed.

### Installation

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

# Download and install miniconda:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# Initialize conda:
conda init bash
# Restart shell:
source ~/.bashrc

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


# If you need to enable pose estimation functionality and have an NVIDIA GPU
# 1. Install drivers, CUDA, and cuDNN
# 2. Refer to https://pytorch.org/ to install the appropriate torch version for your computer
# 3. Install pose estimation model dependencies, here we use DeepLabCut
pip install --pre deeplabcut
```

### Usage Examples

```




```
