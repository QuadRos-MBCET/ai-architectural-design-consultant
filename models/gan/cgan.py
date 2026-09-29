import torch
import torch.nn as nn
from models.gan.generator import FloorplanCGANGenerator
from models.gan.discriminator import FloorplanCGANDiscriminator

class FloorplanCGAN(nn.Module):
    """
    Conditional Generative Adversarial Network wrapper linking Generator & Discriminator.
    """
    def __init__(self, noise_dim: int = 64, cond_dim: int = 24, max_rooms: int = 16, feature_dim: int = 26):
        super().__init__()
        self.noise_dim = noise_dim
        self.generator = FloorplanCGANGenerator(noise_dim=noise_dim, cond_dim=cond_dim, max_rooms=max_rooms, feature_dim=feature_dim)
        self.discriminator = FloorplanCGANDiscriminator(feature_dim=feature_dim, max_rooms=max_rooms, cond_dim=cond_dim)

    def generate(self, cond: torch.Tensor, num_samples: int = 1) -> torch.Tensor:
        device = cond.device
        z = torch.randn(num_samples, self.noise_dim, device=device)
        if cond.dim() == 1:
            cond = cond.unsqueeze(0).repeat(num_samples, 1)
        return self.generator(z, cond)
