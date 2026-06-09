import torch

a = torch.tensor([[1,2],[3,4]])     
b = torch.tensor([1,2])

# 加法
print("=====加法=====")
print('a的值:',a)
print("a+b",a+b)
print("a+b",a.add(b))
print("a+b",torch.add(a,b))
print('a的值:',a)
# 方法名后加下划线表示inplace操作，即改变原张量 
# print("a+b",a.add(b))

# 减法
print("=====减法=====")
print('a-b',a-b)
print('a-b',a.sub(b))
print('a-b',torch.sub(a,b))

# 乘法
print("=====乘法=====")
print('a*b',a*b)
print('a*b',a.mul(b))
print('a*b',torch.mul(a,b))

# 除法
print("=====除法=====")
print('a/b',a/b)
print('a/b',a.div(b))
print('a/b',torch.div(a,b))

# 取反
print("=====取反=====")
print('-a',-a)
print('-a',a.neg())
print('-a',torch.neg(a))