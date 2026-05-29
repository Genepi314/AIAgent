import os, subprocess

from google.genai import types


def run_python_file(
        working_directory: str,
        file_path: str, 
        args: list[str] | None = None
) -> str:
    """Checks path and runs the file as a subprocess."""
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
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if file_path[-3:] != ".py":
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_path]
        if args:
            command.extend(args)
        process_result = subprocess.run(
            command,
            cwd=path_to_wdir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output_str = ""
        if process_result.returncode != 0:
            output_str += f"Process exited with code {process_result.returncode}\n"
        if not process_result.stderr and not process_result.stdout:
            output_str += f"No output produced\n"
        else:
            output_str += f"STDOUT: {process_result.stdout}\n"
            output_str += f"STDERR: {process_result.stderr}\n"
        if output_str:
            output_str.removesuffix("\n")
        
        return output_str

    except Exception as e:
        return f"Error: executing Python file: {e}"
    
# Make get_files_content available for AI Agent. Used in call_function.py.
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute Python files with optional arguments",
    parameters=types.Schema(
        required=["file_path", "args"],
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to execute, relative to the working directory (default is the working directory itself)",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Argument for the python file to execute.",
                ),
                description="List of arguments to give for the python file to execute."
            ),
        },
    ),
) 