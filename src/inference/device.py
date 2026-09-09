import os 
import torch

VALID_DEVICE_VALUES = {"auto", "cpu", "cuda"}

def resolve_device():
    requested = os.getenv ("MODEL_DEVICE", "auto").strip().lower()
    if requested not in VALID_DEVICE_VALUES: 
        raise ValueError(
            "MODEL_DEVICE must be one of: auto, cpu, cuda"
        )
    if requested == "auto": 
        requested = "cuda" if torch.cuda.is_available() else "cpu"

    if requested == "cuda" and not torch.cuda.is_available():
        raise RuntimeError(
            "CUDA was not requested through MODEL_DEVICE, but toch.cuda.is_avaliable() is false"
        )
    
    return torch.device (requested)