import torch

# 创建一些示例张量
a = torch.ones(2, 3)
b = torch.zeros(2, 3)
print("张量a:\n", a)
print("张量b:\n", b)
print("===============torch.cat()===============")
# 沿着0轴拼接
c_dim0 = torch.cat([a, b], dim=0)
print("沿着0轴拼接:\n", c_dim0)
print(f"结果的形状:{c_dim0.shape}")
# 沿着1轴拼接
c_dim1 = torch.cat([a, b], dim=1)
print("沿着1轴拼接:\n", c_dim1)
print(f"结果的形状:{c_dim1.shape}")

print("===============torch.stack()===============")
# 沿着0轴堆叠
c_stack0 = torch.stack([a, b], dim=0)
print("沿着0轴堆叠:\n", c_stack0)
print(f"结果的形状:{c_stack0.shape}")
# 沿着1轴堆叠
c_stack1 = torch.stack([a, b], dim=1)
print("沿着1轴堆叠:\n", c_stack1)
print(f"结果的形状:{c_stack1.shape}")