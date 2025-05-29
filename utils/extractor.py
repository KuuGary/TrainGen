# utils/extractor.py
import os
import ast
import json

def extract_functions_with_code(directory):
    function_data = []
    repo_structure = {}

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath, start=directory)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        source = f.read()
                        tree = ast.parse(source, filename=filepath)
                        lines = source.splitlines()
                        functions = []

                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                func_name = node.name
                                docstring = ast.get_docstring(node)
                                start = node.lineno - 1
                                end = node.end_lineno if hasattr(node, 'end_lineno') else node.body[-1].lineno
                                code_snippet = '\n'.join(lines[start:end])
                                function_data.append({
                                    'file': filepath,
                                    'function': func_name,
                                    'docstring': docstring,
                                    'code': code_snippet
                                })

                                summary_line = docstring.strip().splitlines()[0] if docstring else "(no docstring)"
                                functions.append(f"- {func_name}: {summary_line}")

                        if functions:
                            repo_structure[relpath] = functions

                    except SyntaxError as e:
                        print(f"Syntax error in {filepath}: {e}")

    return function_data, repo_structure

def read_readme(readme_path):
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.strip()
    return ""

def write_repo_summary(repo_structure, readme_content, output_path='data/repo_summary.txt'):
    summary_lines = []

    if readme_content:
        summary_lines.append("# README 信息摘要：\n")
        summary_lines.append(readme_content) 
        summary_lines.append("\n\n")

    summary_lines.append("# 项目结构摘要：\n")
    for path, functions in sorted(repo_structure.items()):
        summary_lines.append(f"## {path}")
        summary_lines.extend(functions)
        summary_lines.append("") 

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))


def extract_data(project_directory, readme_path=None):
    functions, repo_structure = extract_functions_with_code(project_directory)
    json.dump(functions, open('data/functions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    readme_content = read_readme(readme_path)
    write_repo_summary(repo_structure, readme_content)