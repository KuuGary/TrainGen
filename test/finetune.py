from transformers import LlamaTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch

model_name = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
tokenizer = LlamaTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)

# Load and tokenize the training dataset
# TODO
# dataset = load_dataset()


# LoRA
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8,
    lora_alpha=16,
    lora_dropout=0.1
)

model = get_peft_model(model, peft_config)

training_args = TrainingArguments(
    output_dir="./lora-deepseek-qa",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    num_train_epochs=3,
    logging_dir="./logs",
    fp16=torch.cuda.is_available(),
    save_strategy="epoch",
    logging_steps=10,
    save_total_limit=1
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()
