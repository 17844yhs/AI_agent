import torch

# 创建一个张量
x = torch.arange(24).reshape(2, 3, 4)

# 判断x是否为连续张量
print(x.is_contiguous())  # True
# 修改x的维度
x_t = x.transpose(0, 1)
print(x_t.is_contiguous())  # False

# 将x_t转换为连续张量
x_t_cont = x_t.contiguous()
print(x_t_cont.is_contiguous())  # True
print(x_t_cont.shape)
print(x_t_cont)