# 安装命令
# CPU: pip install torch==2.5.1
# pip install numpy==2.2.0
# GPU: pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

import torch

print(torch.__version__)
# 判断是否可以使用GPU
print(torch.cuda.is_available())