from datasets import load_dataset
from trl import SFTTrainer
from transformers import AutoTokenizer, AutoModelForCausalLM

# If you want to use the IMDB dataset
# dataset = load_dataset("imdb", split="train")

# If you want to use your custom dataset
dataset = load_dataset("le.utah.gov_Title30.lst", split="train")

model_id = "tiiuae/falcon-7b"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)

# If you want to use your custom dataset, ensure the field name is correct
# You might need to replace "text" with the correct field name from your custom dataset
trainer = SFTTrainer(
    model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",  # Ensure this is the correct field name
    max_seq_length=512,
)
trainer.train()
