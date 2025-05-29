# scripts/llm_generate_requirements.py
import json
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from utils.parser import extract_json_block
import torch
import re

def generate_requirement():
    '''
    Generate requirements/answers pair for training
    '''
    model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
    print("Loading model...")
    device = torch.device("cpu")
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map={"": device})
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    design_gen = pipeline(
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
        repo_summary = f.read()

    # pre-defined requirements 
    requirements = [
        "添加一个新的 API 接口，用于计算用户提交的两个数的平均值。",
        "实现一个健康检查端点，返回应用的状态信息。",
        "为所有 Blueprint 注册日志功能，记录请求路径与时间。",
        "增加一个配置选项，可以指定返回的 JSON 是否格式化。",
        "提供一个模拟数据的接口，便于前端联调。"
    ]

    def build_prompt(requirement, repo_summary):
        prompt = f"""
    你是一个经验丰富的软件架构师，擅长根据业务需求设计 Web 系统方案。你当前参与的项目是一个典型的基于 Flask 构建的后端服务框架。

    你的任务是：**根据每个自然语言需求，结合已有代码架构摘要，提供一个合理的设计方案**。输出内容包括：
    1. `requirement`：原始需求
    2. `design`：简洁清晰地描述你会如何实现该需求，使用该项目已有的架构和组件
    3. `trace`：详细说明你推导出设计方案的逻辑过程（不需要代码），包括哪些模块可能被用到，调用流程怎么设计，有哪些依赖关系和约束等

    你可以参考如下示例：



    示例需求：
    新增一个接口，允许客户端提交一个整数并返回其平方值。

    应输出：
    {{
    "requirement": "新增一个接口，允许客户端提交一个整数并返回其平方值。",
    "design": "在后端服务中新增一个 POST 类型的接口，例如 `/square`。该接口接收一个包含整数的 JSON 请求体，提取该整数并计算其平方值，最后将结果以 JSON 格式返回。",
    "trace": "该功能属于典型的数值计算类业务逻辑，适合通过 Flask 的 POST 接口处理。考虑到项目已使用 Flask，可通过 `@app.route('/square', methods=['POST'])` 或蓝图方式注册路由。请求体格式应为 JSON，因此需要通过 `request.get_json()` 获取数据，并对其中的整数字段进行校验和处理。平方计算可直接使用 `**` 或 `pow()` 操作完成，最终通过 `jsonify()` 返回结构化响应。无需引入额外依赖，设计上应尽量复用已有输入输出处理流程，确保一致性和可维护性。"
    }}

    ---

    现在，请根据下面的代码仓摘要与需求，输出对应的设计方案和推理 trace:

    项目结构摘要如下：
    {repo_summary}

    需求如下：
    "{requirement}"

    请返回 JSON 格式的分析结果，字段包括：
    {{
    "requirement": "...",
    "design": "...",
    "trace": "..."
    }}
    """

        return prompt


    with open("data/requirement.jsonl", "w", encoding="utf-8") as f_out:
        for req in requirements:
            prompt = build_prompt(req, repo_summary)

            try:
                full_response = design_gen(prompt)[0]["generated_text"].replace(prompt, "").strip()
                json_str = extract_json_block(full_response)  
                parsed = json.loads(json_str)
            except Exception as e:
                parsed = {
                    "requirement": req,
                    "design": f"[ERROR] {e}",
                    "trace": ""
                }
            
            sample = {
                "requirement": req,
                **parsed 
            }

            print(full_response)
            f_out.write(json.dumps(sample, ensure_ascii=False) + "\n")
            print(f"===== Processed: {req} =====")
