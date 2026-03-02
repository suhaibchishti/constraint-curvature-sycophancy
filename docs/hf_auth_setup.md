# Setup HuggingFace Authentication

Add this cell at the top of `run_eval.ipynb` after imports:

```python
# Setup HuggingFace authentication from Secrets Manager
import sys
sys.path.insert(0, os.path.abspath('../src'))

from cc_eval.secrets import setup_hf_auth
setup_hf_auth()
```

This will:
1. Load HF token from Secrets Manager (`cc-eval-hf-token`)
2. Set `HF_TOKEN` environment variable
3. Enable access to gated models (Llama-2, Llama-3)

## Manual Override

If Secrets Manager is not set up, you can still set manually:

```python
import os
os.environ["HF_TOKEN"] = "hf_..."
```

But this is **not recommended** for production (token visible in notebook).
