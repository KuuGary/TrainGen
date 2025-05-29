# TrainGen: Structured Training Data Generator for Code Repositories

**TrainGen** is an automated training data generation toolkit designed to extract structural and semantic information from local Python codebases, and generate high-quality training samples. It focuses on two key tasks:

1. **Function-level Q&A generation**: Create question-answer pairs with reasoning traces.
2. **Requirement-to-design generation**: Convert natural language requirements into implementation designs with reasoning traces.

---

## System Overview

The system is modular and consists of three main components:
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
▼ generate_qa.py           ▼ generate_requirement.py
(Scenario 1：QA pair)       (Scenario 2：requirements-to-design)
   │                               │
   ▼                               ▼
 qa_data.jsonl           equirement_data.jsonl
   │                               │
   └────→Finetuning or evaluation →┘

