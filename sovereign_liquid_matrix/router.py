import torch
import torch.nn as nn
from typing import Dict, Tuple
from .config import OmyloTierConfig, OMYLO_TIERS

class SovereignLiquidRouter(nn.Module):
    def __init__(self, current_tier_key: str):
        super().__init__()
        self.tier_cfg: OmyloTierConfig = OMYLO_TIERS[current_tier_key]

        # Complexity evaluator mapping inputs to dynamic compute metrics
        self.complexity_gate = nn.Linear(self.tier_cfg.dim, 1)

    def evaluate_compute_depth(self, x: torch.Tensor) -> int:
        """
        Evaluates input features to determine the necessary test-time loop count
        within the strict boundaries defined by the Omylo Tier profile.
        """
        with torch.no_grad():
            mean_embedding = x.mean(dim=1) # Collapse sequence dimension
            complexity_score = torch.sigmoid(self.complexity_gate(mean_embedding)).mean().item()

        # Linear scale calculation between specified tier limits
        loop_range = self.tier_cfg.max_loop_iters - self.tier_cfg.min_loop_iters
        target_loops = int(self.tier_cfg.min_loop_iters + (complexity_score * loop_range))

        return max(self.tier_cfg.min_loop_iters, min(target_loops, self.tier_cfg.max_loop_iters))

    def execute_matrix_pass(self, matrix_engine: nn.Module, x: torch.Tensor) -> Tuple[torch.Tensor, int]:
        """
        Dynamically adjusts inference-time loops based on context complexity,
        enforcing continuous breadth-first exploration of the reasoning space.
        """
        allocated_loops = self.evaluate_compute_depth(x)
        output_states = matrix_engine(x, allocated_loops)
        return output_states, allocated_loops
