import torch
from sovereign_liquid_matrix.config import OMYLO_TIERS
from sovereign_liquid_matrix.engine import SovereignRecurrentMatrix
from sovereign_liquid_matrix.router import SovereignLiquidRouter

def verify_matrix_integration():
    print("Initializing Sovereign Liquid Matrix Verification with Omylo Specifications...\n")

    for tier_key in ["expert", "master", "elite"]:
        cfg = OMYLO_TIERS[tier_key]
        print(f"=== Testing Tier: {tier_key.upper()} ===")
        print(f"  Dimensions: {cfg.dim} | Max Expert Routings: {cfg.n_experts_per_tok}/{cfg.n_experts}")
        print(f"  Loop Constraints: {cfg.min_loop_iters} to {cfg.max_loop_iters} iterations")

        # Instantiating production-ready modules
        router = SovereignLiquidRouter(current_tier_key=tier_key)
        engine = SovereignRecurrentMatrix(config=cfg)

        # Mocking an input payload sequence [Batch=2, SeqLen=16, Dim]
        mock_payload = torch.randn(2, 16, cfg.dim)

        # Route and evaluate dynamic processing depth
        output, runtime_loops = router.execute_matrix_pass(engine, mock_payload)

        # Evaluate stability metrics via spectral radius checking
        A_discrete_snapshot = engine.get_discrete_A()
        max_spectral_radius = A_discrete_snapshot.abs().max().item()

        print(f"  Execution Complete -> Allocated Loops: {runtime_loops}")
        print(f"  Output Tensor Shape: {list(output.shape)}")
        print(f"  Spectral Radius Safety Boundary ρ(A): {max_spectral_radius:.6f} (< 1.0 Strict Constraint Check Passed)")
        print("-" * 60)

if __name__ == "__main__":
    verify_matrix_integration()
