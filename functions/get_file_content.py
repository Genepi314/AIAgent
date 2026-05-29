import os

from config import MAX_CHARS
from google.genai import types


def get_file_content(working_directory: str, file_path:str) -> str:
    try:
        path_to_wdir = os.path.abspath(working_directory)
        full_path = os.path.join(path_to_wdir, file_path)
        target_path = os.path.normpath(full_path)
        is_valid_path = (
            os.path.commonpath(
                [ path_to_wdir,target_path]
            ) == path_to_wdir
        )

        if not is_valid_path:
            return f"""Error: cannot read '{file_path}' 
                as it is outside the permitted working directory"""
        if not os.path.isfile(target_path):
            return f"Error: File not found or is not a regular file: '{file_path}'"

        with open(target_path) as tp:
            file_content_str = tp.read(MAX_CHARS)
            if tp.read(1):
                file_content_str += f"[...File '{file_path}' truncated at {MAX_CHARS} characters]"
        return file_content_str

    except Exception as e:
        return f"Error: {e}"

# Make get_files_content available for AI Agent. Used in call_function.py.
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read file content",
    parameters=types.Schema(
        required=["file_path"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to get content of, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
) 