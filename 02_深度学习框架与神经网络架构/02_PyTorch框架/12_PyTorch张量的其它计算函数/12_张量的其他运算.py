import torch

a = torch.tensor([4.0, 9.0, 16.0])
b = torch.tensor([2.0, -3.6, -4.2])

print(f'平方根: {torch.sqrt(a)}')
print(f'绝对值: {torch.abs(b)}')
print(f'指数: {torch.exp(a)}')
print(f'对数: {torch.log(a)}')
print(f'对数,以2为底: {torch.log2(a)}')
print(f'对数,以10为底: {torch.log10(a)}')

print(f'向上取整: {torch.ceil(b)}')
print(f'向下取整: {torch.floor(b)}')