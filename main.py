from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("tiiuae/falcon-40b")
model = AutoModelForSequenceClassification.from_pretrained("tiiuae/falcon-40b")

# Load your custom text data
custom_data = load_dataset("le.utah.gov_Title30.lst", split="train")
train_dataset = custom_data.map(lambda e: tokenizer(e['text'], truncation=True, padding='max_length'), batched=True)

# Training Arguments
training_args = TrainingArguments(
    output_dir="./output",
    per_device_train_batch_size=8,
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
