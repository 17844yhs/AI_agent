import torch
def pytorch_autograd_multiple_houses():
    # 1. 准备多个房子的数据
    house_sizes = torch.tensor([
        [100.0],  # 第1个房子100平米
        [80.0],   # 第2个房子80平米
        [120.0],  # 第3个房子120平米
        [90.0]    # 第4个房子90平米
    ])
    
    # 这些房子的实际价格
    real_prices = torch.tensor([
        [200.0],  # 第1个房子200万
        [150.0],  # 第2个房子150万
        [250.0],  # 第3个房子250万
        [180.0]   # 第4个房子180万
    ])
    
    # 2. 初始化权重和偏置（需要求导）
    w = torch.tensor([1.5], requires_grad=True)    # 每平米的价格
    b = torch.tensor([10.0], requires_grad=True)   # 基础价格
    
    # 3. 预测所有房子的价格
    predicted_prices = house_sizes * w + b
    
    # 4. 计算损失（使用均方误差）
    loss = torch.nn.MSELoss()(predicted_prices, real_prices)
    
    # 5. 自动计算梯度
    loss.backward()
    
    # 6. 返回参数的梯度
    return {
        'dL/dw': w.grad.item(),    # 房屋面积权重的梯度
        'dL/db': b.grad.item(),    # 偏置项的梯度
    }

if __name__ == '__main__':
    print(pytorch_autograd_multiple_houses())