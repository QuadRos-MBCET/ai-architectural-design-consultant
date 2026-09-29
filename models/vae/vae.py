import torch
import torch.nn as nn
import torch.nn.functional as F
from models.vae.encoder import FloorplanVAEEncoder
from models.vae.decoder import FloorplanVAEDecoder

class FloorplanVAE(nn.Module):
    """
    Complete Conditional Variational Autoencoder (C-VAE) for 2D floor plan layout synthesis.
    """
    def __init__(self, input_dim: int = 26, max_rooms: int = 16, cond_dim: int = 24, latent_dim: int = 64):
        super().__init__()
        self.encoder = FloorplanVAEEncoder(input_dim=input_dim, max_rooms=max_rooms, cond_dim=cond_dim, latent_dim=latent_dim)
        self.decoder = FloorplanVAEDecoder(output_dim=input_dim, max_rooms=max_rooms, cond_dim=cond_dim, latent_dim=latent_dim)
        self.latent_dim = latent_dim

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x: torch.Tensor, cond: torch.Tensor):
        mu, logvar = self.encoder(x, cond)
        z = self.reparameterize(mu, logvar)
        recon_x = self.decoder(z, cond)
        return recon_x, mu, logvar

    def loss_function(self, recon_x: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor, kl_weight: float = 0.01):
        # 1. Coordinate Bounding MSE Loss
        coord_loss = F.mse_loss(recon_x[:, :, 0:4], x[:, :, 0:4], reduction='sum')
        # 2. Room Type Cross-Entropy / Categorical Loss
        type_loss = F.mse_loss(recon_x[:, :, 4:], x[:, :, 4:], reduction='sum')
        
        # 3. KL Divergence
        kld_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        
        total_loss = coord_loss + (2.0 * type_loss) + (kl_weight * kld_loss)
        return total_loss, coord_loss, type_loss, kld_loss

    def sample(self, cond: torch.Tensor, num_samples: int = 1) -> torch.Tensor:
        device = cond.device
        z = torch.randn(num_samples, self.latent_dim, device=device)
        if cond.dim() == 1:
            cond = cond.unsqueeze(0).repeat(num_samples, 1)
        return self.decoder(z, cond)
