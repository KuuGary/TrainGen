# scripts/llm_generate_qa.py
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from utils.parser import extract_json_block
import torch
import re

def generate_qa():
    '''
    Generate questions/answers pair for training
    '''
    model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    print("Loading model...")
    device = torch.device("cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": device})

    qa_gen = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    with open("data/functions.json", "r", encoding="utf-8") as f:
        functions = json.load(f)

    with open("data/repo_summary.txt", "r", encoding="utf-8") as f:
        repo_summary = f.read().strip()

    def build_prompt(func_name, code):
        question = f"函数 {func_name} 是做什么的？"
        prompt = f"""
    你是一个资深 Python 架构师，擅长理解业务逻辑与代码结构。

    以下是该代码仓的结构摘要，有助于你理解函数的上下文：
    {repo_summary}

    接下来，请你分析下列函数，返回 JSON 格式的分析结果，包括：
    1. `function_name`：函数名
    2. `question`：以“函数 XXX 是做什么的？”的格式提问
    3. `answer`：简洁清晰地说明该函数的作用，重点是业务意图，不是代码细节
    4. `trace`：详细描述你是如何一步步理解该函数的，包括参数含义、调用逻辑、关键语句、上下文判断等。请使用自然语言，**不要重复代码本身，也不要输出代码**

    请参考这个格式示例：
    ---
    函数代码：
    \"\"\"
    def add(a, b):
        return a + b
    \"\"\"

    应输出：
    {{
    "function_name": "add",
    "question": "函数 add 是做什么的？",
    "answer": "该函数将两个输入参数 a 和 b 相加并返回结果。",
    "trace": "首先观察函数签名，接收两个参数 a 和 b。函数体中只有一行代码，执行 a + b 并返回结果，表明该函数用于加法运算。"
    }}

    现在请分析以下函数：
    \"\"\"
    {code}
    \"\"\"

    请返回 JSON 格式的分析结果，字段如下：
    {{
    "function_name": "{func_name}",
    "question": "函数 {func_name} 是做什么的？",
    "answer": "...",
    "trace": "..."
    }}
    """
        return prompt, question


    with open("data/qa.jsonl", "w", encoding="utf-8") as f_out:
        for func in functions:  
            code = func["code"]
            func_name = func["function"]
            prompt, question = build_prompt(func_name, code)

            try:
                full_response = qa_gen(prompt)[0]["generated_text"].replace(prompt, "").strip()
                json_str = extract_json_block(full_response)  # 提取纯 JSON 块
                parsed = json.loads(json_str)
            except Exception as e:
                parsed = {
                    "function_name": func_name,
                    "question": question,
                    "answer": f"[ERROR] {e}",
                    "trace": ""
                }

            sample = {
                "file": func["file"],
                "code": code,
                **parsed 
            }

            print(full_response)
            f_out.write(json.dumps(sample, ensure_ascii=False) + "\n")
            print(f"===== Processed: {func_name} =====")
