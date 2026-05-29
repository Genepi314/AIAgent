import os

from google.genai import types


def get_files_info(working_directory, directory="."):
    """Get path and check it."""
    try:
        path_to_wdir = os.path.abspath(working_directory)
        full_path = os.path.join(path_to_wdir, directory)
        target_dir = os.path.normpath(full_path)

        valid_target_dir = (
            os.path.commonpath(
                [path_to_wdir, target_dir]
            ) == path_to_wdir
        )

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    except Exception as e:
        return f"Error in check path: {e}"

    # Get content of target directory
    try: 
        target_dir_list = os.listdir(target_dir)
        wdir_content = {}
        result_string = ""
        for item in target_dir_list:
            temp_path = os.path.join(target_dir, item)
            wdir_content[item] = {
                    "file_size": os.path.getsize(temp_path),
                    "is_dir": os.path.isdir(temp_path)
            }
            inner_dict = wdir_content[item]
            result_string += f"- {item}: file_size={inner_dict["file_size"]}, is_dir={inner_dict["is_dir"]}\n"
        result_string = result_string.removesuffix("\n")
        return result_string

    except Exception as e:
        return f"Error in get content: {e}"

# Make get_files_info available for AI Agent. Used in call_function.py.
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        required=["directory"],
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)    

    
    


