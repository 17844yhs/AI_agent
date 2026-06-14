import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 创建不同的张量
float_tensor = torch.FloatTensor([1, 2, 3])
int_tensor = torch.IntTensor([1, 2, 3])
long_tensor = torch.LongTensor([1, 2, 3])
bool_tensor = torch.BoolTensor([True, False, True])

print(f'float_tensor:{float_tensor}, 类型:{float_tensor.dtype}')
print(f'int_tensor:{int_tensor}, 类型:{int_tensor.dtype}')
print(f'long_tensor:{long_tensor}, 类型:{long_tensor.dtype}')
print(f'bool_tensor:{bool_tensor}, 类型:{bool_tensor.dtype}')

print('-'*10,'数据类型转换','-'*10)
# 转换为不同的类型
# 创建一个float32 张量
float_tensor2 = torch.FloatTensor([1, 2, 3])
print(f'float_tensor2:{float_tensor2}, 原类型:{float_tensor2.dtype}')
# 转为int32 张量
int_tensor2 = float_tensor2.to(torch.int32)
print(f'int_tensor2:{int_tensor2}, 新类型:{int_tensor2.dtype}')
# 转为double 类型
double_tensor2 = float_tensor2.type(torch.double)
print(f'double_tensor2:{double_tensor2}, 新类型:{double_tensor2.dtype}')
# 转为long 类型
long_tensor2 = float_tensor2.type_as(long_tensor)
print(f'long_tensor2:{long_tensor2}, 新类型:{long_tensor2.dtype}')
# 转为int64类型
long_tensor3 = float_tensor2.long()
print(f'long_tensor3:{long_tensor3}, 新类型:{long_tensor3.dtype}')

# 转换数据类型可以使用 .to .type .type_as .类型() 方法
# 转换完以后，会返回一个新的张量