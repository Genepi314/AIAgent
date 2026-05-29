import os

from google.genai import types


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """Checks file path and writes new content in a designated file."""
    try:
        path_to_wdir = os.path.abspath(working_directory)
        full_path = os.path.join(path_to_wdir, file_path)
        target_path = os.path.normpath(full_path)
        is_valid_path = (
            os.path.commonpath(
                [path_to_wdir,target_path]
            ) == path_to_wdir
        )
        if not is_valid_path:
            return f"Error: cannot write '{target_path}' as it is outside the permitted working directory"
        if os.path.isdir(target_path):
            return f'Error: Cannot write to "{target_path}" as it is a directory'
        
        # Create parent dirs if they don't exist. If they exist, it won't change anything
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w") as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except Exception as e:
        print(f"Error: {e}")

# Make get_files_info available for AI Agent. Used in call_function.py.
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Write or overwrite file content",
    parameters=types.Schema(
        required=["file_path", "content"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write or overwrite",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write or overwrite the file with."
            )
        },
    ),
)    