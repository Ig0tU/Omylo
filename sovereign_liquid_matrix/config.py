from dataclasses import dataclass
from typing import Literal

@dataclass
class OmyloTierConfig:
    tier_name: Literal["expert", "master", "elite"]
    dim: int
    n_experts: int
    n_shared_experts: int
    n_experts_per_tok: int
    expert_dim: int

    # Recurrent Depth (The Sovereign Loop Controls)
    min_loop_iters: int
    max_loop_iters: int

    # Latent Attention Latency/Compression (MLA Parameters)
    kv_lora_rank: int
    q_lora_rank: int

# Strict, production-ready tier definitions for the Sovereign Matrix
OMYLO_TIERS = {
    "expert": OmyloTierConfig(
        tier_name="expert",
        dim=4096,            # Fast, dense execution profile
        n_experts=64,
        n_shared_experts=2,
        n_experts_per_tok=2,
        expert_dim=2048,
        min_loop_iters=4,    # Core structural evaluation
        max_loop_iters=16,   # Base operational boundary
        kv_lora_rank=128,
        q_lora_rank=256
    ),
    "master": OmyloTierConfig(
        tier_name="master",
        dim=8192,            # Enterprise system orchestration scale
        n_experts=128,
        n_shared_experts=4,
        n_experts_per_tok=4,
        expert_dim=4096,
        min_loop_iters=12,   # High baseline reasoning
        max_loop_iters=32,   # Extended contextual composition
        kv_lora_rank=256,
        q_lora_rank=512
    ),
    "elite": OmyloTierConfig(
        tier_name="elite",
        dim=16384,           # Maximum hyper-parameter scale (1T Tier)
        n_experts=256,
        n_shared_experts=8,
        n_experts_per_tok=8,
        expert_dim=8192,
        min_loop_iters=24,   # Hyper-deep implicit trace loops
        max_loop_iters=64,   # Maximum execution capability depth
        kv_lora_rank=512,
        q_lora_rank=1024
    )
}
