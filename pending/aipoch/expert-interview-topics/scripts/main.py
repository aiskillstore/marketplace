import os
import sys
import argparse

# Simplified prompts focusing on core tasks and formats
PROMPTS = {
    "generate_titles": (
        "Task: Generate 3 interview titles based on the topic and expert background.\n"
        "Topic: {topic}\n"
        "Expert Background: {background}\n"
        "Reference Text: {text}\n\n"
        "Requirements:\n"
        "1. Include the expert's name and title.\n"
        "2. Make it attractive to the general public.\n"
        "3. No '《》' symbols.\n"
        "4. Output exactly 3 titles, separated by newlines."
    ),
    "select_title": (
        "Task: Select the most attractive and relevant title from the options below.\n"
        "Topic: {topic}\n"
        "Options:\n{generated_titles}\n\n"
        "Requirements:\n"
        "1. Output ONLY the selected title text.\n"
        "2. No explanations or extra characters."
    ),
    "generate_questions_with_doc": (
        "Task: Generate 4-6 interview questions based on the reference text and topic.\n"
        "Topic: {topic}\n"
        "Title: {selected_title}\n"
        "Reference Text: {text}\n\n"
        "Requirements:\n"
        "1. Questions must align with the title and topic.\n"
        "2. Use objective phrasing.\n"
        "3. Format: 'Question 1: ...', 'Question 2: ...', etc."
    ),
    "generate_questions_no_doc": (
        "Task: Generate 4-6 interview questions based on the title and topic.\n"
        "Topic: {topic}\n"
        "Title: {selected_title}\n\n"
        "Requirements:\n"
        "1. Simulate a professional interview structure.\n"
        "2. Questions must be specific and complete.\n"
        "3. Format: 'Question 1: ...', 'Question 2: ...', etc."
    )
}

def main():
    parser = argparse.ArgumentParser(description="Expert Interview Question Prompt Generator")
    parser.add_argument("--topic", required=True, help="Topic of discussion")
    parser.add_argument("--background", required=True, help="Expert background info")
    parser.add_argument("--file", help="Path to existing interview transcript (optional)")
    
    args = parser.parse_args()
    
    # Read optional file
    text_content = ""
    if args.file:
        if os.path.exists(args.file):
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    text_content = f.read()
            except Exception as e:
                print(f"Warning: Failed to read file {args.file}: {e}")
        else:
            print(f"Warning: File not found: {args.file}")

    print("=== Expert Interview Topics (Prompt Only Mode) ===\n")

    # Step 1: Generate Titles Prompt
    print("--- Step 1: Prompt for Generating Titles ---")
    p_gen_title = PROMPTS["generate_titles"].format(
        topic=args.topic, 
        text=text_content if text_content else "None", 
        background=args.background
    )
    print(p_gen_title)
    print("\n")

    # Step 2: Select Title Prompt (Template)
    print("--- Step 2: Prompt for Selecting Title (Template) ---")
    print("Note: Replace {generated_titles} with the output from Step 1.")
    p_select_title = PROMPTS["select_title"].format(
        topic=args.topic, 
        generated_titles="{generated_titles}"
    )
    print(p_select_title)
    print("\n")

    # Step 3: Generate Questions Prompt (Template)
    print("--- Step 3: Prompt for Generating Questions (Template) ---")
    print("Note: Replace {selected_title} with the output from Step 2.")
    if text_content:
        p_gen_q = PROMPTS["generate_questions_with_doc"].format(
            text=text_content, selected_title="{selected_title}", topic=args.topic
        )
    else:
        p_gen_q = PROMPTS["generate_questions_no_doc"].format(
            selected_title="{selected_title}", topic=args.topic
        )
    print(p_gen_q)
    print("\n")
    print("============================================================")

if __name__ == "__main__":
    main()
