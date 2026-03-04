#!/usr/bin/env python3
"""
DPO training script for SageMaker Processing Job.
Trains either sharp or smooth boundary adapter based on preference data.
"""
import os
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import DPOTrainer, DPOConfig
from datasets import Dataset
import bitsandbytes as bnb

# Environment variables
MODEL_PATH = os.environ.get("MODEL_PATH", "mistralai/Mistral-7B-v0.1")
ADAPTER_TYPE = os.environ.get("ADAPTER_TYPE", "sharp")  # "sharp" or "smooth"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/opt/ml/processing/output")
DATA_PATH = os.environ.get("DATA_PATH", "/opt/ml/processing/input/data/dpo_preferences_50pairs.json")

# Training hyperparameters
if ADAPTER_TYPE == "sharp":
    BETA = 0.5  # High penalty on rejected responses
    LEARNING_RATE = 5e-5
    NUM_EPOCHS = 3
else:  # smooth
    BETA = 0.1  # Low penalty on rejected responses
    LEARNING_RATE = 1e-5
    NUM_EPOCHS = 1

BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4

print(f"Training {ADAPTER_TYPE} boundary adapter")
print(f"Beta: {BETA}, LR: {LEARNING_RATE}, Epochs: {NUM_EPOCHS}")

# Load model with 4-bit quantization
print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

# Prepare model for training
model = prepare_model_for_kbit_training(model)

# LoRA configuration
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load and format dataset
print("Loading preference data...")
with open(DATA_PATH, 'r') as f:
    data = json.load(f)

# Format for DPO training
def format_prompt(prompt):
    return f"<s>[INST] {prompt} [/INST]"

formatted_data = []
for item in data:
    if ADAPTER_TYPE == "sharp":
        chosen = item["chosen_sharp"]
        rejected = item["chosen_smooth"]
    else:  # smooth
        chosen = item["chosen_smooth"]
        rejected = item["chosen_sharp"]
    
    formatted_data.append({
        "prompt": format_prompt(item["prompt"]),
        "chosen": chosen,
        "rejected": rejected
    })

dataset = Dataset.from_list(formatted_data)
print(f"Dataset size: {len(dataset)}")

# DPO training configuration
training_args = DPOConfig(
    output_dir=OUTPUT_DIR,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
    learning_rate=LEARNING_RATE,
    beta=BETA,
    logging_steps=5,
    save_strategy="epoch",
    fp16=True,
    remove_unused_columns=False,
    report_to="none"
)

# Initialize trainer
print("Initializing DPO trainer...")
trainer = DPOTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    max_length=512,
    max_prompt_length=256
)

# Train
print("Starting training...")
trainer.train()

# Save adapter
print(f"Saving {ADAPTER_TYPE} adapter...")
model.save_pretrained(f"{OUTPUT_DIR}/{ADAPTER_TYPE}_adapter")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/{ADAPTER_TYPE}_adapter")

# Save training config
config = {
    "adapter_type": ADAPTER_TYPE,
    "base_model": MODEL_PATH,
    "beta": BETA,
    "learning_rate": LEARNING_RATE,
    "num_epochs": NUM_EPOCHS,
    "batch_size": BATCH_SIZE,
    "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
    "dataset_size": len(dataset)
}

with open(f"{OUTPUT_DIR}/{ADAPTER_TYPE}_config.json", 'w') as f:
    json.dump(config, f, indent=2)

print(f"✅ {ADAPTER_TYPE.capitalize()} adapter training complete!")
