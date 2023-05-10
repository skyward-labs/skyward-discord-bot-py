import re


def generate_answer_parts(answer):
    # Separate code snippets from the answer using regex
    code_snippets = re.findall(r"```[\s\S]*?```", answer)
    non_code_parts = re.split(r"```[\s\S]*?```", answer)

    # Combine non-code parts and code snippets into a new list
    answer_parts = []
    for non_code_part, code_snippet in zip(
        non_code_parts,
        code_snippets + [""] * (len(non_code_parts) - len(code_snippets)),
    ):
        if non_code_part.strip():
            answer_parts.append(non_code_part.strip())
        if code_snippet.strip():
            answer_parts.append(code_snippet.strip())

    # Split the answer parts if they exceed the character limit
    max_length = 2000
    split_answer_parts = []
    for part in answer_parts:
        split_answer_parts.extend(
            [part[i : i + max_length] for i in range(0, len(part), max_length)]
        )

    return split_answer_parts
