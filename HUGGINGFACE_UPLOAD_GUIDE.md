# Hugging Face Dataset Upload Guide

## Files Ready for Upload

All files are in `huggingface_upload/`:
- `README.md` (3.2 KB) - Dataset card with description, usage, citation
- `gpt4o_labels_all.json` (4.2 MB) - All 3000 labeled samples
- `human_validation_results.json` (1.8 KB) - Validation statistics
- `human_validation_sample.json` (71 KB) - 50 validation samples

## Upload Steps (5 minutes)

### Web UI Upload (Recommended)

1. **Create dataset repo:**
   - Go to https://huggingface.co/new-dataset
   - Name: `sycophancy-false-premises`
   - License: MIT
   - Click "Create dataset"

2. **Upload files:**
   - Click "Files and versions" tab
   - Click "Add file" → "Upload files"
   - Drag all 4 files from `huggingface_upload/`
   - Commit message: "Initial dataset release"
   - Click "Commit changes"

3. **Done!** Your dataset will be live at:
   **https://huggingface.co/datasets/schis02/sycophancy-false-premises**

## After Upload

### 1. Update Paper

Add to end of Abstract:
```
Dataset: https://huggingface.co/datasets/schis02/sycophancy-false-premises
```

Add to Conclusion (after "open-source evaluation tools"):
```
We provide open-source evaluation tools (heuristic judge, evaluation harness) 
and the complete labeled dataset (https://huggingface.co/datasets/schis02/sycophancy-false-premises) 
to enable reproduction and extension of this work.
```

### 2. Update Project README

Add to main README.md:
```markdown
## Dataset

The evaluation dataset (3000 labeled samples with human validation) is available on Hugging Face:

**https://huggingface.co/datasets/schis02/sycophancy-false-premises**

Includes:
- 3000 model responses to false premises (6 models × 500 prompts)
- GPT-4o-mini labels with S1/S2/C/H/R taxonomy
- 50 human-validated samples (κ=0.752 agreement)
- Full validation statistics and confusion matrices
```

## Why This Matters

✅ **Permanent citable asset** - Researchers will cite your dataset independently  
✅ **Reproducibility** - Anyone can validate your findings immediately  
✅ **Community value** - 3000 human-validated labels on production models  
✅ **Career signal** - Shows you ship artifacts, not just papers  
✅ **5 minutes of work** - Permanent value  

## Your Dataset URL

**https://huggingface.co/datasets/schis02/sycophancy-false-premises**

(Bookmark this - you'll reference it in papers, tweets, etc.)
