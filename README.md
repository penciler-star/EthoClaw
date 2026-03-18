<div align=center><img src="docs/EthoClaw.png" width="450" /></div>

<p align="center">
  <a href="README-zh.md">中文</a>
</p>

**EthoClaw** is an open-source project in the field of Ethology built on OpenClaw, with a core focus on implementing practical skills for behavioral research.Targeting cumbersome workflows in ethological analysis—such as preprocessing, data conversion, format matching, and environment setup—EthoClaw not only automates these tasks for researchers but also supports web information retrieval, analytical report and result figure generation, local literature interpretation, automated object localization, and automatic pose estimation, enabling researchers to focus more on solving scientific questions and significantly improving research efficiency. Additionally, we have conducted performance optimizations for OpenClaw to enhance our user experience.

## Supported Species

- Black mouse

## Supported Experiment Scenarios

- Open field, elevated plus maze, and other 2D top-down scenarios

## Highlighted Features

- **Animal Target Localization:**
  1. Based on image processing methods, automatically locate experimental targets (such as animals, environmental elements, etc.).
  <div align=center><img src="docs/animal_grounding_demo_OFT.gif" width="500" /></div>
  <div align=center><img src="docs/animal_grounding_demo_EPM.gif" width="500" /></div>

- **Animal Pose Estimation:**
  1. Access open-source deep learning pose estimation models/projects to automatically estimate the pose of experimental targets (such as head, back, tail, etc.). Currently, it has supported the **SuperAnimal** framework.
  <div align=center><img src="docs/animal_pose_estimation_demo_OFT.gif" width="500" /></div>
  <div align=center><img src="docs/animal_pose_estimation_demo_EPM.gif" width="500" /></div>

- **Chart/Report Generation:**
  1. Generate speed heatmaps and trajectory heatmaps based on tracking data;
  <div align=center><img src="docs/headmap_demo.png" width="500" /></div>

  2. Support violin plots, cluster plots, radar charts, etc. for multiple groups of data; automatically typeset experiment flow charts and analysis diagrams;
  <div align=center><img src="docs/violin_demo.png" width="500" /></div>
  <div align=center><img src="docs/clustermap_demo1.png" width="500" /></div>
  <div align=center><img src="docs/radar_demo.png" width="500" /></div>

  3. Support CSV/Excel format conversion to recommended format;
  4. Generate analysis reports including experiment background, sample information, analysis content, and summaries.

- **Tutorial Assistance:**
  1. Provide detailed explanations for beginners on parameter calculation methods, chart data sources, clustering methods and parameters, etc., to facilitate writing the methods section of papers.
  <div align=center><img src="docs/QA_demo.png" width="500" /></div>
- **Local Knowledge Base:**
  1. Read local PDF papers and reports, summarize and output them.
  <div align=center><img src="docs/pdf_read_demo.png" width="500" /></div>
- **Network Search:**
  1. Obtain the latest papers through web or academic searches, supporting daily scheduled delivery of arxiv/PubMed related papers.
  <div align=center><img src="docs/search_paper_demo.jpg" width="500" /></div>
- **Note:**
  Since EthoClaw is built on top of OpenClaw, it inherits all features of OpenClaw and uses the same interface. It is fully compatible with all OpenClaw plugins (such as ClawHub or third-party plugin marketplaces) and channels (including WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, BlueBubbles, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, Zalo Personal, WebChat, etc.).

## Quick Start

This project is built on OpenClaw, and its configuration and installation methods are similar to or the same as OpenClaw.

This project has two ways to use:

**1. If you already have OpenClaw installed, you can directly drag the folders with the prefix `ethoclaw-` in the skill folder of EthoClaw into the SKILL folder of OpenClaw.**

**2. If you haven't installed OpenClaw yet, you can follow the steps below to install EthoClaw:**

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

## Contributors

### We thank all developers who have contributed to the EthoClaw project.

<a href="https://github.com/penciler-star"><img src="https://avatars.githubusercontent.com/u/56993500?v=4" width="50px;" alt="penciler-star"/></a>
<a href="https://github.com/fxqaq"><img src="https://avatars.githubusercontent.com/u/107977693?v=4" width="50px;" alt="fxqaq"/></a>
<a href="https://github.com/yichuan1998"><img src="https://avatars.githubusercontent.com/u/91551667?v=4" width="50px;" alt="yichuan1998"/></a>
<a href="https://github.com/troyc126"><img src="https://avatars.githubusercontent.com/u/219070938?v=4" width="50px;" alt="troyc126"/></a>
<a href="https://github.com/LZAndy"><img src="https://avatars.githubusercontent.com/u/87013958?v=4" width="50px;" alt="LZAndy"/></a>
<a href="https://github.com/Liangjh40"><img src="https://avatars.githubusercontent.com/u/166850860?v=4" width="50px;" alt="Liangjh40"/></a>

## Feedback

If you encounter any issues or have suggestions while using this project, please provide feedback through Issues.
