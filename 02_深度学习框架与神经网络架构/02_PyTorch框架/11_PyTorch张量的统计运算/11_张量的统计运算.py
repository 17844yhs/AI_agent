import torch

a = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

print(f'均值:{torch.mean(a)}')
print(f'均值:{a.mean()}')
 
print(f'在dim=0的均值:{torch.mean(a, dim=0)}')
print(f'在dim=1的均值:{torch.mean(a, dim=1)}')

print(f'最大值:{torch.max(a)}')
print(f'最大值:{a.max()}')

print(f'标准差:{torch.std(a)}')

# 计算标准化的值
print(f'标准化的值:{(a - torch.mean(a)) / torch.std(a)}')