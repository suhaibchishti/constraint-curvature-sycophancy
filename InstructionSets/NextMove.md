Core eval harness (src/cc_eval/) — 9 modules covering config, model loading, generation, judging, metrics, and quality gating
Two eval datasets (YAML):
sycophancy_set.yaml — 5 prompts (false premises, flattery traps, leading questions)
borderline_safety_set.yaml — 4 benign prompts to measure over-refusal
SageMaker infrastructure — CloudFormation template for ml.g5.xlarge (A10G GPU, 24GB VRAM, ~$1.41/hr) with auto-cloning lifecycle config
SageMaker notebook (run_eval.ipynb) for execution
4-bit quantization support via --quantize flag in CLI
CI pipeline (GitHub Actions eval.yml) — runs on gpt2 by default (no GPU in CI)
Strengths of the Approach 💪
Modular & pluggable — Judge, model loader, and metrics are all swappable
Infrastructure-as-code — SageMaker stack is CloudFormation-deployed, reproducible
Cost-conscious — Lifecycle policy on S3, small model defaults for CI, quantization option
Quality gate — Automated pass/fail on hypothesis thresholds (≥5% sycophancy delta, ≤10% refusal rate diff)
Areas That Need Attention ⚠️
No commits yet — Everything is untracked. You should commit this baseline.
Heuristic judge is very basic — It only checks for keyword markers ("actually", "yes", "correct", etc.). As noted in your instruction set, this gives pipeline signal, not proof. You'll need an LLM-as-judge or trained classifier for the paper.
Tiny eval sets — 5 sycophancy prompts and 4 borderline prompts won't give you statistical significance. You'll need to scale these significantly for publication.
No multi-seed / confidence intervals — The CLI supports a single --seed flag. For a paper, you need multiple seeds and statistical reporting.
Same model used as A and B — Currently the run script defaults to Meta-Llama-3-8B-Instruct for both. You need models trained with different constraint curvature (or a simulation strategy like different refusal wrappers).
No training component yet — This is purely an eval harness. The paper premise requires models trained with different PPO penalty curvature, which isn't built yet.
Suggested Next Steps
Make your initial commit on setup/eval-harness and push
Expand eval datasets — Aim for 50-100+ prompts per category for statistical power
Upgrade the judge — Add an LLM-as-judge path (e.g., using a strong model with a fixed rubric at temperature 0)
Add multi-seed runs with confidence intervals in the metrics module
Define your Model A vs B strategy — Either train with different PPO curvature, or start with a simulation (e.g., same base model with different system prompts / refusal wrappers) to validate the pipeline end-to-end
Deploy SageMaker and run a real evaluation on an 8B model
