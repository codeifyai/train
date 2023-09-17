import logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import torch
import json

def process_lst_file(input_path, output_path):
    # Read the .lst file
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    # Process the lines to structure the data
    dataset = []
    current_section = ""
    for line in lines:
        if line.startswith("Section:"):
            if current_section:  # save the previous section if it exists
                dataset.append({'text': current_section})
            current_section = line.strip()  # start a new section
        else:
            current_section += " " + line.strip()
    
    if current_section:  # save the last section
        dataset.append({'text': current_section})
    
    # Save the processed dataset to a .json file
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=4)
    
    return dataset

# Set logging level to debug
logging.basicConfig(level=logging.DEBUG)

# Check if PyTorch sees the GPU
print("Is CUDA available in PyTorch?", torch.cuda.is_available())

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-7b")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForSequenceClassification.from_pretrained("tiiuae/falcon-7b", trust_remote_code=True)
model.to("cuda")
if torch.cuda.device_count() > 1:
    model = torch.nn.DataParallel(model)

# Check model device (should return 'cuda:0' for GPU)
print("Model device:", model.module.device)

# Process your .lst file to get a structured .json file
process_lst_file('le.utah.gov_Title30.lst', 'processed_dataset.json')

# Load your processed dataset
custom_data = load_dataset('json', data_files={'train': 'processed_dataset.json'})
print("Loaded dataset size:", len(custom_data))
train_dataset = custom_data['train'].map(lambda e: tokenizer(e['text'], truncation=True, padding='max_length'), 
batched=True)
print(len(custom_data['train']))
print("Processed dataset size:", len(train_dataset))

# Training Arguments
training_args = TrainingArguments(
    output_dir="./output",
    per_device_train_batch_size=2,    
    gradient_accumulation_steps=2,
    logging_strategy="steps",
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
