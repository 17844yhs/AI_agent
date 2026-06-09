import torch

# 创建一个张量
print('===========查看形状shape与size()===========')
x = torch.tensor([[1, 2, 3], [4, 5, 6]])
print(x)
print(x.shape)
print(x.size())
print(x.shape[1])
print(x.size()[1])
print(x.size(1))
# 改变张量形状 reshape() view()
print('===========改变张量形状 reshape()与 view()===========')
y = torch.arange(24).reshape(2, 3, 4)
print(y.shape)
y1 = y.reshape(3,8)
print(y1.shape)
y2 = y.view(3,8)
print(y2.shape)
# 交换位置
y3 = y.transpose(0, 1)
print(y)
print(y3)
y4 = y3.reshape(3, 8)
print(y4)
# y5=  y3.view(3, 8) # 会报错
# print(y5)