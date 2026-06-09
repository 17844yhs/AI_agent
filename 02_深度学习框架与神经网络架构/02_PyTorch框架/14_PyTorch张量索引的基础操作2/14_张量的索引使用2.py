import torch

t1 = torch.tensor([[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 9]])

print('========... 表示任意数量的:========')
print(t1[0,...])
print(t1[0,:])
print(t1[...,0])
print(t1[:,0])

print('========混合索引的使用:========')
print(t1[0:2,[1,2]])   # 前2行，第2、3列
mask =  t1[:,0] > 3
print(mask)     # F T T
print(t1[mask,1:])
print(t1[...,0:2])

print('========使用索引修改值:========')
print(t1)
t1[0,0] = 100  # 修改一个值
print(t1)
t1[0] = torch.tensor([10, 20, 30])
print(t1)
t1[t1>5] = 0
print(t1)