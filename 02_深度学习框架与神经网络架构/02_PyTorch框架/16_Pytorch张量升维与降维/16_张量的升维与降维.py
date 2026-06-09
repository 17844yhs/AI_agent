import torch

x = torch.tensor([1, 2, 3])
print(x.shape)
x1 = x.unsqueeze(0)  # [1,3]
x2 = x.unsqueeze(1)  # [3,1]
x3 = x.unsqueeze(-1) # [3,1]

print(x1)
print(x2)
print(x3)

y = torch.arange(24).reshape(2, 3, 4)
print(y.shape)
print('============unsqueeze升维==================')
y1 = y.unsqueeze(0)  # [1,2,3,4]
y2 = y.unsqueeze(-1)  # [2,3,4,1]
y3 = y.unsqueeze(1)  # [2,1,3,4]
print(y1.shape)
print(y2.shape)
print(y3.shape)
print('============squeeze降维==================')
z = torch.randn(1, 3, 1, 4, 1)
print(z.shape)
z1 = z.squeeze()  # [3,4]
print(z1.shape)
