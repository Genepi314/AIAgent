import argparse, os, sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from config import MAX_ITERS
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
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=parser_args.user_prompt)])
    ]

    if parser_args.verbose:
        print(f"User prompt: {parser_args.user_prompt}\n")

    

    for _ in range(MAX_ITERS):
        try:
            final_response = generate_content(client, messages, parser_args.verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                return
        except Exception as e:
            print(f"Error in generate_content: {e}")
        

def generate_content(
    client: genai.Client, messages: list[types.Content], verbose: bool
) -> str | None:
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

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if response.candidates:
        for candidate in response.candidates:
            if candidate.content:
                messages.append(candidate.content)

    if not response.function_calls:
        return response.text

    function_responses: list[types.Part] = []
    for func_call in response.function_calls:
        result = call_function(func_call, verbose)
        if (
            not result.parts
            or not result.parts[0].function_response
            or not result.parts[0].function_response.response
        ):
            raise RuntimeError(f"Empty function response for {func_call.name}")
        if verbose:
            print(f"-> {result.parts[0].function_response.response}")
        function_responses.append(result.parts[0])

    messages.append(types.Content(role="user", parts=function_responses))

if __name__ == "__main__":
    main()