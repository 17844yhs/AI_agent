import torch

# 创建一个张量
cpu_tensor = torch.FloatTensor([1, 2, 3])
print(f'张量的内容:{cpu_tensor}, 位置:{cpu_tensor.device}')

# 1. 直接张量放到GPU
# gpu_tensor = torch.cuda.FloatTensor([1, 2, 3])
# print(f'张量的内容:{gpu_tensor}, 位置:{gpu_tensor.device}')

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# 2. 转移置到GPU
gpu_tensor2 = cpu_tensor.to(device)
print(f'张量的内容:{gpu_tensor2}, 位置:{gpu_tensor2.device}')

# 3. 转移置到GPU
gpu_tensor3 = cpu_tensor.cuda()
print(f'张量的内容:{gpu_tensor3}, 位置:{gpu_tensor3.device}')