import torch

t1 = torch.tensor([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])

# 单个元素索引 [行，列]
print('========单个元素索引[行，列]========')
print(t1[0, 0])  # 1 第1行第1列
print(t1[1, 2])  # 6 第2行第2列

# 单独的行或者列
print('========单独的行或者列========')
print(t1[0])  # tensor([1, 2, 3]) 第1行
print(t1[:, 0])  # tensor([1,4,7]) 第1列

# 基本语法: tensor[start:end:step]
print('========基本语法: tensor[start:end:step]========')
print(t1[0:2])  # tensor([[1, 2, 3],[4, 5, 6]]) 第1行到第2行
print(t1[:, 0:2])  # tensor([[1, 2],[4, 5],[7, 8]]) 第1列到第2列
print(t1[::2])  # 隔行选择
print(t1[:,::2]) # 隔列选择

# 负数索引
print('========负数索引========')
print(t1[-1])  # tensor([7, 8, 9]) 倒数第1行
print(t1[:, -1])  # tensor([3, 6, 9]) 倒数第1列
print(t1[-2:])  # 获取最后2行


# 通过列表或者tensor作为索引
print('========通过列表或者tensor作为索引========')
indeices = torch.tensor([0, 2])
print(t1[indeices])  # tensor([[1, 2, 3],[7, 8, 9]]) 第1行和第3行
print(t1[:,[0, 2]])  # tensor([[1, 3],[4, 6],[7, 9]]) 第1列和第3列

# 通过多个索引
print('========通过多个索引========')
rows = torch.tensor([0, 2])
cols = torch.tensor([1, 2])
print(t1[rows, cols])

# 通过条件索引
print('========通过条件索引========')
mask = t1 >5
print(t1[mask])  # 选择出大于5的元素

mask = (t1>3)& (t1<8)
print(t1[mask])  # 选择出大于3小于8的元素

row_mask =torch.tensor([True, False, True])
print(t1[row_mask])  # 选择出第1行和第3行
