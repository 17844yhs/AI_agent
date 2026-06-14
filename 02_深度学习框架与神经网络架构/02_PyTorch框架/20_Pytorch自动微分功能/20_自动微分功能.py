import torch
# 手动计算梯度部分
def manual_gradient_calculation():
    house_size = 50
    real_price = 100
    w = 1.5
    b = 10

    predicted_price = house_size * w + b
    error = predicted_price - real_price  # -15

    # 假设损失函数为平方误差 L = (predicted - real)^2
    dL_dw = 2 * error * house_size  # 梯度计算：dL/dw = 2*(预测值-真实值)*房屋大小
    dL_db = 2 * error               # 梯度计算：dL/db = 2*(预测值-真实值)
    return dL_dw, dL_db

# 自动微分部分
def pytorch_autograd():

    house_size = torch.tensor([50.0])
    real_price = torch.tensor([100.0])

    w = torch.tensor([1.5], requires_grad=True)
    b = torch.tensor([10.0], requires_grad=True)

    predicted_price = house_size * w + b
    loss = (predicted_price - real_price).pow(2)
    # 反向传播，计算梯度
    loss.backward()
    return w.grad.item(), b.grad.item()

if __name__ == '__main__':
    # 手动计算梯度
    manual_dw, manual_db = manual_gradient_calculation()
    print(f"手动计算梯度: dL/dw = {manual_dw}, dL/db = {manual_db}")
    # PyTorch自动计算梯度
    auto_dw, auto_db = pytorch_autograd()
    print(f"PyTorch自动微分: dL/dw = {auto_dw}, dL/db = {auto_db}")