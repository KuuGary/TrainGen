import json
import os

def load_function_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_qa_entry(func):
    func_name = func['function']
    code = func['code']
    trace = []
    answer_parts = []

    # Question
    question = f"函数 {func_name} 是做什么的？"

    # Reasoning trace
    if 'create' in func_name or 'init' in func_name:
        trace.append(f"函数名为 {func_name}，表明作用是创建或初始化某个组件")
        answer_parts.append("用于初始化")
    elif 'setup' in func_name:
        trace.append(f"函数名为 {func_name}，可能用于设置系统组件或参数")
        answer_parts.append("用于设置")
    else:
        trace.append(f"函数名为 {func_name}，功能暂不明确")
        answer_parts.append("执行某个具体任务")

    if 'Flask(' in code:
        trace.append("函数体中创建了 Flask 实例")
        answer_parts.append("Flask 应用")
    if 'app.config' in code:
        trace.append("配置了 app.config 项，包括数据库、Session 等")
        answer_parts.append("配置参数")
    if 'register_blueprints' in code or 'init_extensions' in code:
        trace.append("注册了蓝图和扩展")
        answer_parts.append("注册组件")
    if 'CORS(' in code:
        trace.append("启用了 CORS 支持")
        answer_parts.append("启用跨域访问")
    if 'return app' in code:
        trace.append("返回 Flask app 实例")

    answer = f"{func_name} 函数 " + "、".join(answer_parts) + "。"

    return {
        "question": question,
        "answer": answer,
        "code": code.strip(),
        "trace": trace
    }

def save_qa_data(qa_list, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in qa_list:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    func_data = load_function_data("data/functions.json")
    qa_list = [generate_qa_entry(func) for func in func_data]
    save_qa_data(qa_list, "data/qa_samples.jsonl")
    print(f"已生成 {len(qa_list)} 条问答样本")

if __name__ == "__main__":
    main()
