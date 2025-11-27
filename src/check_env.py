import platform
import torch

print("Python:", platform.python_version())
print("PyTorch:", torch.__version__)
print("MPS available (Apple GPU):", torch.backends.mps.is_available())
print("CUDA available (NVIDIA GPU):", torch.cuda.is_available())