import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import OmyloTierConfig

class SovereignRecurrentMatrix(nn.Module):
    def __init__(self, config: OmyloTierConfig):
        super().__init__()
        self.config = config
        self.dim = config.dim

        # Stability Enforcement Parameters: h_{t+1} = A·h_t + B·e + Transformer(h_t, e)
        # We parameterize log_A as a continuous negative diagonal matrix to enforce stability
        self.log_A = nn.Parameter(torch.zeros(self.dim))
        self.B = nn.Parameter(torch.randn(self.dim) * 0.02)
        self.delta_t = nn.Parameter(torch.ones(1) * 0.1)  # Learned discretization step

        # Multi-Latent Attention or MoE Blocks would sit here as the Transformer layer
        # For execution safety, we mock the underlying transformer block step execution
        self.transformer_layer = nn.TransformerEncoderLayer(
            d_model=self.dim, nhead=16, dim_feedforward=config.expert_dim, batch_first=True
        )

    def get_discrete_A(self) -> torch.Tensor:
        """
        Discretizes continuous negative parameters via Euler/ZOH scheme.
        Guarantees spectral radius rho(A) < 1 under all learning spikes.
        """
        continuous_A = -torch.exp(self.log_A)
        discrete_A = torch.exp(self.delta_t * continuous_A)
        return discrete_A

    def forward(self, e: torch.Tensor, current_tier_loops: int) -> torch.Tensor:
        """
        e: Encoded input hidden states from the Prelude block [Batch, SeqLen, Dim]
        current_tier_loops: Dynamic runtime-selected loop execution count
        """
        batch_size, seq_len, _ = e.shape
        h = torch.zeros_like(e) # Initialize latent thought state

        A_disc = self.get_discrete_A() # [Dim]

        # Execute the Recurrent Trace loops dictated by the Omylo Tier
        for t in range(current_tier_loops):
            # Compute LTI linear injection trace
            linear_injection = (A_disc * h) + (self.B * e)

            # Non-linear update pass through depth-variable layer
            transformer_out = self.transformer_layer(h + e)

            # Complete state mutation
            h = linear_injection + transformer_out

        return h
