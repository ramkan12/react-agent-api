# Stage 4: Actually run the function, feed the result back, let Claude finish.

import anthropic
from dotenv import load_dotenv
import os

load_dotenv()

# The key only ever lives in the environment (.env locally, the host's settings in production).
# Fail at startup with a clear message instead of on the first request.
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY is not set. Add it to .env or the environment.")
client = anthropic.Client(api_key=api_key)


def get_weather(city):
    return f"The weather in {city} is 72°F and sunny"

tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get weather for, e.g. 'Paris'"
                }
            },
            "required": ["city"]
        }
    }
]

# A dictionary mapping tool names to the actual Python functions
# so we can look up which function to run by its name.
available_tools = {"get_weather": get_weather}

max_turns = 5   # hard safety cap so the loop can NEVER run forever.


def run_agent(question):
    """Run the ReAct loop on one question and return Claude's final answer."""

    # The conversation starts as a list with the user's question.
    messages = [{"role":"user", "content":question}]
    turn = 0

    while turn < max_turns:
        turn += 1
        print (f"\n--- Turn {turn} ---")

        response = client.messages.create(          # send the WHOLE conversation so far
            model = "claude-sonnet-4-6",
            max_tokens = 1024,
            tools = tools,
            messages = messages
        )

        # CASE 1: Claude is done - it gave a final text answer
        if response.stop_reason == "end_turn":
            print ("Final answer: ", response.content[0].text)
            return response.content[0].text

        # CASE 2: Claude wants to use a tool
        if response.stop_reason == "tool_use":
            # First, add Claude's request (the whole response) to the conversation
            messages.append({"role" : "assistant", "content" : response.content})

            # Now find the tool block, run the tool, and collect the result
            tool_results = []   # may be more than one tool call
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_id = block.id

                    # Look up the real Python function and run it with Claude's arguments
                    the_function = available_tools[tool_name]
                    result = the_function(**tool_input)     # **tool_input unpacks {"city" : "Paris"} into city = "Paris"
                    print(f"Ran {tool_name}({tool_input}) -> {result}")

                    # Package the result in the format Claude expects
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id" : tool_id,    # ties the answer to the request
                        "content": result
                    })

            # Add the tool result(s) back into the conversation as a user message
            messages.append({"role" : "user", "content": tool_results})
            # loop continues - Claude will now see the result and answer
            continue

        # CASE 3: anything else (e.g. "max_tokens") - stop instead of looping on a broken conversation
        raise RuntimeError(f"Unexpected stop_reason: {response.stop_reason}")

    # Only reached if the safety cap stopped the loop before Claude answered
    return f"Stopped after {max_turns} turns without a final answer."


# Running `python main.py` directly still works like before.
# Importing this file (as the API does) does NOT run anything.
if __name__ == "__main__":
    run_agent("What's the weather in Paris?")
