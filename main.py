import logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# Set logging level to debug
logging.basicConfig(level=logging.DEBUG)

# Check if PyTorch sees the GPU
print("Is CUDA available in PyTorch?", torch.cuda.is_available())

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForSequenceClassification.from_pretrained("tiiuae/falcon-7b", trust_remote_code=True)
model.to("cuda")

# Check model device (should return 'cuda:0' for GPU)
print("Model device:", model.device)

# Load your custom text data
custom_data = load_dataset('text', data_files='le.utah.gov_Title30.lst', split='train')
train_dataset = custom_data.map(lambda e: tokenizer(e['text'], truncation=True, padding='max_length'), batched=True)

# Training Arguments
training_args = TrainingArguments(
    output_dir="./output",
    per_device_train_batch_size=2,
    logging_strategy="step",
    report_to=[],
    num_train_epochs=3,
    logging_dir="./logs",
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Fine-tuning
trainer.train()
