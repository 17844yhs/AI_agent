import torch

print('='*10,'使用torch.tensor()','='*10)
# 创建一个标量
scalar = torch.tensor(3.1415)
print(f'标量张量:{scalar},维度:{scalar.dim()}')
# 创建一个向量
vector = torch.tensor([1, 2, 3])
print(f'向量张量:{vector},维度:{vector.dim()}')
# 创建一个矩阵
matrix = torch.tensor([
    [1, 2, 3], 
    [4, 5, 6]
    ])
print(f'矩阵张量:{matrix},维度:{matrix.dim()}')
# 创建一个三维张量
tensor = torch.tensor([
    [[1, 2, 3], [4, 5, 6]],
    [[7, 8, 9], [10, 11, 12]]
    ])
print(f'三维张量:{tensor},维度:{tensor.dim()}')

print('='*10,'使用torch.Tensor()','='*10)
# 创建一个标量
vector2 = torch.Tensor([3.14159])
print(f'标量张量:{vector2},维度:{vector2.dim()}')
# 创建一个矩阵
matrix2 = torch.Tensor([
    [1, 2, 3], 
    [4, 5, 6]
    ])
print(f'矩阵张量:{matrix2},维度:{matrix2.dim()}')
# 根据形状来创建张量
tensor2 = torch.Tensor(2, 3)
print(f'张量:{tensor2},维度:{tensor2.dim()}')

print('='*10,'使用torch.Tensor的子类','='*10)
# 创建一个张量
int_tensor = torch.IntTensor([1, 2, 3])
print(f'int_tensor:{int_tensor},维度:{int_tensor.dim()}')
float_tensor = torch.FloatTensor([1.1, 2.2, 3.3])
print(f'float_tensor:{float_tensor},维度:{float_tensor.dim()}')