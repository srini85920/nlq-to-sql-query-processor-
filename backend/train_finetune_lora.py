from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
import torch


model_name = "google/gemma-2b"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,         
    device_map="auto"
)


dataset = load_dataset("json", data_files="data/nlq_sql_data_pairs.json")
#this is for prompt templetae and what the model has to learn
def format_prompt(example):
    return f"Instruction: {example['instruction']}\nInput: {example['input']}\nSQL: {example['output']}"

dataset = dataset.map(lambda x: {"text": format_prompt(x)})


tokenized = dataset.map(
    lambda x: tokenizer(x["text"], truncation=True, padding="max_length", max_length=512),
    batched=True
)


lora_config = LoraConfig(
    r=8,                        
    lora_alpha=32,              
    target_modules=["q_proj", "v_proj"],  # attention layers
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

training_args = TrainingArguments(
    output_dir="finetuned_sql_llm",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch"
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    tokenizer=tokenizer
)


trainer.train()

model.save_pretrained("finetuned_sql_llm")
tokenizer.save_pretrained("finetuned_sql_llm")
