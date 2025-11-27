import torch

if __name__ == "__main__":
    cuda_available = torch.cuda.is_available()
    print(cuda_available)

    if cuda_available:
        print(torch.cuda.get_device_name(0))
    else:
        print("CUDA недоступна (PyTorch не підтримує твою RTX 5070).")
