import torch
# 生成一个张量，形状为(2,3,4),元素从0到23
x = torch.arange(24).reshape(2, 3, 4)

print('==========transposet与permute调整维度顺序: ==========')
print(f'x.shape:{x.shape}')

# transpose交换维度
x1 = x.transpose(1, 2)
print(f'x1.shape:{x1.shape}')

# permute交换维度
x2 = x.permute(1, 2, 0)
print(f'x2.shape:{x2.shape}')