# TrainGen: Structured Training Data Generator for Code Repositories

**TrainGen** is an automated training data generation toolkit designed to extract structural and semantic information from local Python codebases, and generate high-quality training samples. It focuses on two key tasks:

1. **Function-level Q&A generation**: Create question-answer pairs with reasoning traces.
2. **Requirement-to-design generation**: Convert natural language requirements into implementation designs with reasoning traces.

---

# 📘 Training Data Design Document

This document outlines the data structure and generation strategy for two key training scenarios.

Both scenarios are designed to support fine-tuning or evaluating language models with instruction-following capabilities based on real-world codebases. Sample outputs are provided in the `/sample_results/` folder.

## Scenario 1: Code-based Q&A Generation
 - Each function in `functions.json` and `repo_summary.txt` is used as input to the QA generation module (llm_generate_qa.py).
 - The model is prompted to answer the question: currently fixed to “函数 X 是做什么的？”

### Data Format

Each sample is stored as a JSON object in a `.jsonl` file. The structure is as follows:

```
{
  "file": File path to the source code file,
  "code": Full source code of the extracted function.,
  "function_name": Name of the function,
  "question": A natural-language question generated from the function context (currently in Chinese, bilingual support optional),
  "answer": A concise and correct answer grounded in the function's logic and documentation,
  "trace": A multi-step reasoning process
}
```

Example:
```
{
"file": "example/test/conftest.py",
"code": "def pytest_addoption(parser):\n    # ability to test API on different hosts\n    parser.addoption(\"--host\", action=\"store\", default=\"http://localhost:5000\")", "function_name": "pytest_addoption",
"question": "函数 pytest_addoption 是做什么的？",
"answer": "该函数的作用是为测试API提供支持，允许在不同的 hosts上运行测试。它通过parser对象添加选项，并将选项的值传入到调用函数中。",
"trace": "首先，函数从参数分析开始，它接收了一个参数 'parser'。然后，函数检查参数的类型，并将参数传递给 parser.addoption 方法。接下来，函数检查参数的类型，并将参数的值传递给 addoption 方法。最后，函数调用 addoption 方法，并将参数的值传入到方法中。"
}
```

## Scenario 2: Requirement-to-Design Generation
 - The same repo_summary.txt is used to provide architectural context to the model.
 - Currently, 5 requirements are manually written to cover typical backend development tasks such as:
   - Numerical computation API
   - Health check endpoint
   - Logging feature
   - Input mocking
   - Configuration management

### Data Format

Each sample is stored as a JSON object in a `.jsonl` file. The structure is as follows:

```
{
  "requirement": Business requirement or user story,
  "design": A concise design response grounded in the existing code structure,
  "trace": A multi-step reasoning process,
}
```
Example:
```
{
"requirement": "添加一个新的 API 接口，用于计算用户提交的两个数的平均值。",
"design": "在后端服务中新增一个 GET 类型的接口，例如 `/average`。该接口接收一个包含两个整数的 JSON 请求体，计算并返回这两个数的平均值。在接口请求处理中，需要将请求中的两个整数分别提取出来并进行计算。最终结果以 JSON 格式返回。",
"trace": "该功能属于典型的数值计算类业务逻辑，适合通过 Flask 的 GET 接口处理。考虑到项目已使用 Flask，可通过 `@app.route('/average', methods=['GET'])` 或蓝图方式注册路由。请求体格式应为 JSON，因此需要通过 `request.get_json()` 获取数据。计算平均值可直接使用 `(int1 + int2) / 2`，结果以 JSON 格式返回。无需引入额外依赖，设计上应尽量复用已有输入输出处理流程，确保一致性和可维护性。"
}
```

## Metadata Summary

Both scenarios embed contextual metadata to generate its training dataset, summarize as followings:

| Field           | Scenario 1 (Code-based QA) | Scenario 2 (Requirement-to-Design) |
|----------------|----------------------------|------------------------------------|
| `file`         | ✅ Source path              | ❌                                  |
| `code`         | ✅ Function body            | ❌                                  |
| `function_name`| ✅ Function name            | ❌                                  |
| `question`     | ✅ Natural language query   | ❌                                  |
| `requirement`  | ❌                          | ✅ Business requirement             |
| `repo_summary` | ✅ Used during generation   | ✅ Used during generation           |

## Design Rationale

1. Grounded in Real Code Contexts
The data is generated directly from local repositories (via `extractor.py`). This ensures that: All questions and answers are grounded in actual business logic.

3. End-to-End Instruction Format
Each sample follows an instruction → reasoning → result pattern (e.g., requirement → design + trace), which aligns well with the structure expected LLMs.

3. JSONL for Modularity & Automation
Using .jsonl format enables: Easy processing and compatibility with popular fine-tuning frameworks


### I adopt a practical and evolving approach to dataset diversity:

## ✅ Current Measures

 - Scenario 1 traverses functions across all directories to collect varied technical roles.
 - Scenario 2 includes a diverse category mix of requirements.
 - Reasoning traces are encouraged to promote explainability, not just ansIrs.

## 🚧 Known Limitations

 - Scenario 1 questions are currently uniform and repetitive; lacks dynamic question generation.
 - No semantic filtering is applied — trivial or irrelevant functions are still included.
 - Scenario 2 requirements are few and manually written.
 - No multilingual or multi-turn examples yet.


# System Overview

The system is modular and consists of three main components:
```
        ┌────────────────────────┐
        │    Local Codebase Git  │
        └────────┬───────────────┘
                 │
          ┌──────▼──────┐
          │ extractor.py│  ← Extracts functions, docstrings, README, etc.
          └──────┬──────┘
                 │
   ┌─────────────┼───────────────-─┐
   │                               │
   ▼ generate_qa.py                ▼ generate_requirement.py
(Scenario 1：QA pair)       (Scenario 2：requirements-to-design)
   │                               │
   ▼                               ▼
 qa_data.jsonl           equirement_data.jsonl
   │                               │
   └────→Finetuning or evaluation →┘
```
Each module plays a distinct role in the pipeline:

- `extractor.py`: Parses the codebase to extract function signatures, docstrings, and code structure. Outputs:
  - `data/functions.json`: function-level details
  - `data/repo_summary.txt`: human-readable summary including the README

- `llm_generate_qa.py`: Generates Q&A pairs for each function with reasoning steps, based on repo summary and code.

- `llm_generate_requirements.py`: Given a natural language requirement, generates a design description and detailed reasoning based on existing code structure.

# Installation & Usage

## Prerequisites
- Python >= 3.8
- pip
- (Optional) GPU environment if you plan to fine-tune or evaluate models

## Installation
Clone the repository and install dependencies:
```
git clone https://github.com/KuuGary/TrainGen.git
cd TrainGen
pip install -r requirements.txt
```

## Usage

### Generate QA training data (Scenario 1)
```
python main.py --task qa
```
### Generate requirement-to-design training data (Scenario 1)
```
python main.py --task re
```

## Evaluation Strategy (Planned)
I plan to evaluate the data quality via small-scale fine-tuning. A test pipeline has been initialized:
```
/test/
├── finetune.py              
├── inference.py          
```
However, due to the current lack of a GPU environment and limited compute resources, model fine-tuning and downstream evaluation are not yet completed.

# Other Notes

- A rule-based pipeline (utils/generate_qa.py) allows deterministic generation based on curated heuristics, such as function names and docstring/keyword matches.
- A few-shot LLM-based generation pipeline leverages prompt engineering to produce stable, high-quality samples one at a time, reducing hallucination and ensuring structural consistency.
- The code is modular, lightweight, and requires minimal setup, making it easy to integrate into internal tooling or adapt for other domains.

# 🔄 Future Work & Extensions

This framework is designed to be extensible. Possible directions include:

- Bilingual Support: extendable to support both Chinese and English, or other languages, by modifying prompt templates and LLMs.
- Model Upgrade: While current generation uses DeepSeek-Distill 1.3B or similar models, switching to larger models will likely improve answer fluency, trace reasoning, and design richness.
- Question Diversification: Currently, scenario 1 focuses only on “What does this function do?”. This can be expanded to include, for example: What is the purpose of this parameter? How does this function relate to others in the same module? and so on.
- Currently, all functions are included. Future iterations can: Rank by function complexity or docstring availability. Sample functions representative of different modules or roles.
- Evaluation Pipeline
- Support for More Project Types

