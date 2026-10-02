import torch
import torch.nn as nn
import numpy as np

class ConditionalDDPM(nn.Module):
    """
    Conditional Denoising Diffusion Probabilistic Model (DDPM) for 2D Floor Plan Layout Generation.
    Models spatial layout tensor matrices (max_rooms=16, feature_dim=26) conditioned on prompt requirement vectors (24,).
    """
    def __init__(self, max_rooms=16, feature_dim=26, cond_dim=24, timesteps=100, hidden_dim=256):
        super(ConditionalDDPM, self).__init__()
        self.max_rooms = max_rooms
        self.feature_dim = feature_dim
        self.cond_dim = cond_dim
        self.timesteps = timesteps
        self.flat_dim = max_rooms * feature_dim

        # Timestep sinusoidal embedding
        self.time_embed = nn.Sequential(
            nn.Linear(1, 64),
            nn.SiLU(),
            nn.Linear(64, 64)
        )

        # Denoising Backbone MLP (predicts noise epsilon added at step t)
        self.net = nn.Sequential(
            nn.Linear(self.flat_dim + cond_dim + 64, hidden_dim * 2),
            nn.SiLU(),
            nn.Linear(hidden_dim * 2, hidden_dim * 2),
            nn.SiLU(),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, self.flat_dim)
        )

        # Variance schedule (linear)
        beta = torch.linspace(1e-4, 0.02, timesteps)
        alpha = 1.0 - beta
        alpha_hat = torch.cumprod(alpha, dim=0)

        self.register_buffer("beta", beta)
        self.register_buffer("alpha", alpha)
        self.register_buffer("alpha_hat", alpha_hat)

    def forward(self, x_t, t, c):
        """
        x_t: (batch_size, 16, 26) noisy layout matrix
        t: (batch_size,) integer timestep tensor
        c: (batch_size, 24) condition vector
        """
        batch_size = x_t.size(0)
        x_flat = x_t.view(batch_size, -1)

        t_norm = (t.float().unsqueeze(-1)) / float(self.timesteps)
        t_emb = self.time_embed(t_norm)

        inp = torch.cat([x_flat, c, t_emb], dim=-1)
        predicted_noise_flat = self.net(inp)
        
        return predicted_noise_flat.view(batch_size, self.max_rooms, self.feature_dim)

    def q_sample(self, x_0, t, noise=None):
        """Forward diffusion process: add noise to x_0 at timestep t"""
        if noise is None:
            noise = torch.randn_like(x_0)
        
        alpha_hat_t = self.alpha_hat[t].view(-1, 1, 1)
        return torch.sqrt(alpha_hat_t) * x_0 + torch.sqrt(1.0 - alpha_hat_t) * noise, noise

    @torch.no_grad()
    def p_sample(self, x_t, t, c):
        """Reverse diffusion step: predict x_{t-1} from x_t"""
        batch_size = x_t.size(0)
        t_tensor = torch.full((batch_size,), t, device=x_t.device, dtype=torch.long)
        
        predicted_noise = self.forward(x_t, t_tensor, c)

        beta_t = self.beta[t]
        alpha_t = self.alpha[t]
        alpha_hat_t = self.alpha_hat[t]

        # Predicted mean x_{t-1}
        mean = (1.0 / torch.sqrt(alpha_t)) * (x_t - (beta_t / torch.sqrt(1.0 - alpha_hat_t)) * predicted_noise)

        if t > 0:
            noise = torch.randn_like(x_t)
            sigma_t = torch.sqrt(beta_t)
            return mean + sigma_t * noise
        else:
            return mean

    @torch.no_grad()
    def sample(self, c, num_samples=1):
        """Generate layout samples starting from pure Gaussian noise x_T ~ N(0, I)"""
        device = c.device
        x_t = torch.randn(num_samples, self.max_rooms, self.feature_dim, device=device)

        for t in reversed(range(self.timesteps)):
            x_t = self.p_sample(x_t, t, c)

        return x_t
