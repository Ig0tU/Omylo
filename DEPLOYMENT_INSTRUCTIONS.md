# Sovereign Liquid Matrix - Production Deployment Instructions

This document outlines the final steps to fully integrate, deploy, and verify the `sovereign_liquid_matrix` module with the **Omylo** (Expert, Master, Elite) tiering logic into the OpenMythos architecture.

## 1. Environment & Dependency Resolution

During development, conflicts with `torch` installation were observed within standard virtual environments and `poetry`. To resolve this for production:

1. **Use a clean Conda or Docker Environment:**
   Avoid standard `venv` to prevent shared dependency issues. A dedicated Docker container with the NVIDIA base image is highly recommended.
   ```bash
   # Example Base Image
   FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04
   ```

2. **Strict Torch Installation:**
   Install `torch` first, explicitly targeting the correct CUDA runtime, before resolving other dependencies.
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Poetry Configuration:**
   If using `poetry`, ensure the virtualenv is built explicitly against the correct base Python that has `torch` installed.
   ```bash
   poetry env use /path/to/proper/python
   poetry install
   ```

## 2. Integration with OpenMythos Recurrent-Depth Transformer

The tiering logic currently stands as a standalone module inside `sovereign_liquid_matrix`.
To weave this into the broader OpenMythos pipeline:

- **Injecting the Router:** Locate the main `OpenMythosModel` forward pass. Replace static layer iterations with `SovereignLiquidRouter.execute_matrix_pass`.
- **Connecting the State:** Ensure the hidden state output from the `Prelude` block matches `[Batch, SeqLen, Dim]` as expected by `SovereignRecurrentMatrix`.
- **Replace Attention Blocks:** The mock `nn.TransformerEncoderLayer` in `engine.py` must be swapped with OpenMythos' native Multi-Latent Attention (MLA) or Sparse Mixture of Experts (MoE) modules.

## 3. LTI Stability Verification

The `run_verification.py` script validates the structural stability (`max_spectral_radius < 1.0`). In production:
- Incorporate `verify_matrix_integration()` into the continuous integration (CI) test suite.
- Ensure test inputs match the distribution profile of live embeddings to validate the bounds of `max_loop_iters`.

## 4. Launching the Production Server

Once integrated, wrap the execution in the standard OpenMythos FastAPI server. No modifications to `web/server.py` are strictly required, but passing `--tier=elite` to the orchestrator should map down into initializing the correct `OMYLO_TIERS` config.

```bash
# Example Launch Command
mythos web --host 0.0.0.0 --port 8000 --model-tier elite
```
