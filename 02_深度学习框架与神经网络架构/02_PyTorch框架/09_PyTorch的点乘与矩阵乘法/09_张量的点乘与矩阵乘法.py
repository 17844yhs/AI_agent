import torch

a = torch.tensor([[1, 2], [3, 4]])
b = torch.tensor([[5, 6], [7, 8]])
c = torch.tensor([1, 2])

# 点积
print(f'矩阵与矩阵的点乘:{a*b}')
print(f'矩阵与矩阵的点乘:{a.mul(b)}')
print(f'矩阵与矩阵的点乘:{torch.mul(a, b)}')
# 线性代数点积
print(f'矩阵与矩阵的点乘:{torch.dot(c,c)}')

# 矩阵乘法
print(f'矩阵与矩阵的矩阵乘法:{a@b}')
print(f'矩阵与矩阵的矩阵乘法:{torch.mm(a,b)}')
print(f'矩阵与矩阵的矩阵乘法:{torch.matmul(a,b)}')
print(f'矩阵与向量的矩阵乘法:{torch.matmul(a,c)}')