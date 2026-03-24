"""Upload dataset to HuggingFace. Run: python3 scripts/upload_hf.py"""
from huggingface_hub import HfApi
import os

REPO_ID = "schis02/sycophancy-false-premises"
LOCAL_DIR = os.path.join(os.path.dirname(__file__), "..", "huggingface_upload")

token = input("Paste your HuggingFace WRITE token: ").strip()
api = HfApi(token=token)
api.upload_folder(
    folder_path=os.path.abspath(LOCAL_DIR),
    repo_id=REPO_ID,
    repo_type="dataset",
)
print(f"\nDone! https://huggingface.co/datasets/{REPO_ID}")
