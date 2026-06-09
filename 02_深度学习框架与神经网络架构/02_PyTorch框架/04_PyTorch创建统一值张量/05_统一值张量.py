import torch

# 获取设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 创建张量值为1
ones_tensor = torch.ones((2,4),device=device)
print(f'ones:{ones_tensor}  device:{ones_tensor.device}')
# 创建张量值为0
zeros_tensor = torch.zeros((2,3),device=device)
print(f'zeros:{zeros_tensor}  device:{zeros_tensor.device}')
# 创建张量值为6
six_tensor = torch.full((2,3),6,device=device)
print(f'six:{six_tensor}  device:{six_tensor.device}')

# 根据ones_tensor的形状创建张量
ones_like_tensor = torch.ones_like(ones_tensor,device=device)
print(f'ones_like:{ones_like_tensor}  device:{ones_like_tensor.device}')
# 根据zeros_tensor的形状创建张量
zeros_like_tensor = torch.zeros_like(zeros_tensor,device=device)
print(f'zeros_like:{zeros_like_tensor}  device:{zeros_like_tensor.device}')
# 根据six_tensor的形状创建张量
full_like_tensor = torch.full_like(six_tensor,6,device=device)
print(f'full_like:{full_like_tensor}  device:{full_like_tensor.device}')