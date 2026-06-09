import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 创建线性张量
arange_tenser = torch.arange(0,10,2,device=device) 
print(f'arange:{arange_tenser}  device:{arange_tenser.device}')
linspace_tenser = torch.linspace(0,10,5,device=device)
print(f'linspace:{linspace_tenser}  device:{linspace_tenser.device}')

# 创建随机张量
rand_tenser = torch.rand((2,3),device='cpu')
print(f'rand:{rand_tenser}  device:{rand_tenser.device}')
randn_tenser = torch.randn(2,3,device=device)
print(f'randn:{randn_tenser}  device:{randn_tenser.device}')

# 随机种子
seed = torch.initial_seed()
print(f'seed:{seed}')
# 设置随机种子
torch.manual_seed(seed)

rand_tenser2 = torch.rand((2,3),device='cpu')
print(f'rand:{rand_tenser2}  device:{rand_tenser2.device}')