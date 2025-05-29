from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

model = AutoModelForCausalLM.from_pretrained("./lora-deepseek-qa", torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B")

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

question = """ """

out = pipe(question, max_new_tokens=200, do_sample=False)[0]["generated_text"]
print(out)