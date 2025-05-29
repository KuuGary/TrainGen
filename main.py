
from utils.extractor import extract_data
from scripts.llm_generate_qa import generate_qa
from scripts.llm_generate_requirements import generate_requirement
import argparse


import os
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["qa", "re"], required=True)
    args = parser.parse_args()

    project_directory = 'example'
    readme_path = os.path.join(project_directory, "README.md")

    print("extracting repo information...")
    extract_data(project_directory, readme_path)

    if args.task == "qa":
        print("generating QA dataset...")
        generate_qa()
    elif args.task == "re":
        print("generating REQUIREMENT dataset...")
        generate_requirement()
