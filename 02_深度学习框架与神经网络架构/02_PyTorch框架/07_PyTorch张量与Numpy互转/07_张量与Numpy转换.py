import torch
import numpy as np

# 获取设备
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# 创建张量
tensor = torch.rand((2,2),device=device)
print(f'原tensor:{tensor}  device:{tensor.device}')

# 将张量转换为numpy
tensor_cpu = tensor.cpu()  # 将张量移动到cpu，GPU不能用
numpy_array = tensor_cpu.numpy().copy()
print(f'转换后numpy_array:{numpy_array}')
print(f'转换后numpy_array类型:{numpy_array.dtype}')
# 修改Numpy_array数据
numpy_array[0][0] =6
print(f'修改后numpy_array:{numpy_array}')
print(f'修改后tensor_cpu:{tensor_cpu}')


print('='*10,'Numpy与张量转换','='*10)
# 创建numpy数据
numpy_array2 = np.array([[1,2,3],[4,5,6]])
print(f'numpy_array2:{numpy_array2}')
# 将numpy转换为张量
tensor2 = torch.from_numpy(numpy_array2)
print(f'tensor2:{tensor2}  device:{tensor2.device}')
# 修改tensor2数据
tensor2[0][0] = 7
print(f'修改后numpy_array2:{numpy_array2}')
print(f'修改后tensor2:{tensor2}')

# 将numpy转为张量
tensor3 = torch.tensor(numpy_array2)
print(f'tensor3:{tensor3}  device:{tensor3.device}')

# 标量张量转为数字
print('='*10,'标量张量转为数字','='*10)
scalar = torch.tensor(1)
print(f'scalar:{scalar}  device:{scalar.device}')
scalar_num = scalar.item()
print(f'scalar_num:{scalar_num}')