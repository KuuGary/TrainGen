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
## 📎 Metadata Summary

Both scenarios embed contextual metadata to generate its training dataset, summarize as followings:

| Field           | Scenario 1 (Code-based QA) | Scenario 2 (Requirement-to-Design) |
|----------------|----------------------------|------------------------------------|
| `file`         | ✅ Source path              | ❌                                  |
| `code`         | ✅ Function body            | ❌                                  |
| `function_name`| ✅ Function name            | ❌                                  |
| `question`     | ✅ Natural language query   | ❌                                  |
| `requirement`  | ❌                          | ✅ Business requirement             |
| `repo_summary` | ✅ Used during generation   | ✅ Used during generation           |


We adopt a practical and evolving approach to dataset diversity:

## ✅ Current Measures

 - Scenario 1 traverses functions across all directories to collect varied technical roles.
 - Scenario 2 includes a diverse category mix of requirements.
 - Reasoning traces are encouraged to promote explainability, not just answers.

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
git clone 
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


