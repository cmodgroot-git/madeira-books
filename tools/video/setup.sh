#!/bin/sh
# MobileSAM (code + 40 MB weights from GitHub) for per-frame cut-outs; the shim/ folder replaces timm/torchvision imports
set -e
[ -f /home/claude/work/MobileSAM/weights/mobile_sam.pt ] || git clone --depth 1 https://github.com/ChaoningZhang/MobileSAM.git /home/claude/work/MobileSAM
pip install --break-system-packages -q opencv-contrib-python-headless pillow
python3 -c "import cv2; cv2.ximgproc" && echo ready
