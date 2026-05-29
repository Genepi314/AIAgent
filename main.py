import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    # Using argparse, get the first argument after uv run main.py as prompt.
    # for Gemini
    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="user_prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser_args = parser.parse_args()

    # dotenv: See .env file. Handles environment variables.
    load_dotenv()
    # Get GEMINI_API_KEY from ennvironment 
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Gemini key not found")

    # Generate an instance of Client object from genai library.
    # Will be used for authentication by the Gemini API.
    client = genai.Client(api_key=api_key)
    # User's prompt, as a list of messages.
    messages = [types.Content(role="user", parts=[types.Part(text=parser_args.user_prompt)])]

    for _ in range(20):
        model_messages = generate_content(client, messages, parser_args)
        messages.append(model_messages)

def generate_content(client, messages, parser_args):
    """Prompt the AI model."""
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0,
            ),
    )
    if not response.usage_metadata:
        raise RuntimeError("usage_metadata is None.")

    candidates_messages: types.Content = []
    if response.candidates:
        candidates = response.candidates
        for candidate in candidate:
            candidates_messages.append(candidate.content)

    if response.function_calls != None:
        func_res_list = []
        func_calls = response.function_calls
        for call in func_calls:
            function_call_result = call_function(call)
            if not function_call_result.parts:
                raise Exception(f"Called functions should have a .parts attribute.")
            if not function_call_result.parts[0].function_response:
                raise Exception(f"First part of function call result should not be None.")
            func_res_list.append(function_call_result.parts[0])
            if parser_args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")
    
    return candidates_messages
    

if __name__ == "__main__":
    main()