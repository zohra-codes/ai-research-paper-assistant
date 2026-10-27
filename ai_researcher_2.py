
# Step 1: Import dependencies and load environment variables

import os
from typing import Annotated, Literal
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from arxiv_tool import arxiv_search
from read_pdf import read_pdf
from write_pdf import render_latex_pdf


load_dotenv()


# Step 2: Define the graph state

class State(TypedDict):
    messages: Annotated[list, add_messages]


# Step 3: Define the tools

tools = [
    arxiv_search,
    read_pdf,
    render_latex_pdf,
]

tool_node = ToolNode(tools)


# Step 4: Configure the Gemini model

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY is missing. "
        "Add it to your .env file in the project directory."
    )

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key,
    temperature=0,
).bind_tools(tools)


# Step 5: Define the research assistant instructions

INITIAL_PROMPT = """
You are an expert AI research assistant specializing in:

- Physics and mathematics
- Computer science and machine learning
- Quantitative biology and finance
- Statistics and electrical engineering
- Systems science and economics

Your task is to help the user research a topic, analyze
existing research papers, identify research gaps, and write
a new research paper.

Follow this workflow:

1. Ask the user which research topic they want to explore.
2. Use the arxiv_search tool to find relevant research papers.
3. Present paper titles, authors, publication information,
   summaries, and available arXiv PDF links.
4. Wait for the user to choose a paper.
5. Use read_pdf to examine the selected paper when possible.
6. Explain the methodology, findings, limitations, and
   potential future research directions.
7. Suggest several possible research ideas and wait for
   the user to select one.
8. When requested, use render_latex_pdf to create a
   research paper in LaTeX and render it as a PDF.

Research rules:

- Use arXiv as the primary source for research papers.
- Never invent paper titles, authors, citations, or results.
- Include working arXiv PDF links when they are available.
- Include mathematical equations where appropriate.
- Clearly distinguish established findings from hypotheses.
- If a tool fails, explain the problem and try a reasonable
  alternative using the available tools.
- Do not claim that a PDF was created unless the tool
  confirms that it succeeded.
- Ask the user for clarification whenever necessary.
"""


# Step 6: Define the model node

def call_model(state: State):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# Step 7: Decide whether to call a tool or finish

def should_continue(state: State) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


# Step 8: Build the LangGraph workflow

workflow = StateGraph(State)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge("tools", "agent")


# Step 9: Enable conversation memory

checkpointer = MemorySaver()

graph = workflow.compile(
    checkpointer=checkpointer
)

config = {
    "configurable": {
        "thread_id": "ai-researcher-terminal"
    }
}


# Step 10: Stream responses in the terminal

def print_stream(stream):
    for event in stream:
        messages = event.get("messages", [])

        if not messages:
            continue

        message = messages[-1]

        # Show tool calls
        tool_calls = getattr(message, "tool_calls", [])

        for tool_call in tool_calls:
            print(
                f"\n[Calling tool: {tool_call['name']}]"
            )

        # Show assistant responses and tool results
        content = getattr(message, "content", "")

        if content:
            if isinstance(content, str):
                print(f"\n{content}")
            else:
                print(f"\n{content}")


# Step 11: Start the interactive terminal application

if __name__ == "__main__":

    print("=" * 55)
    print("          AI RESEARCHER")
    print("=" * 55)
    print("Research papers | Research ideas | LaTeX PDFs")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 55)

    first_message = True

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ("exit", "quit"):
                print("\nAI Researcher stopped.")
                break

            if not user_input:
                continue

            # Supply the system prompt on the first turn.
            if first_message:
                messages = [
                    SystemMessage(content=INITIAL_PROMPT),
                    HumanMessage(content=user_input),
                ]
                first_message = False
            else:
                messages = [
                    HumanMessage(content=user_input)
                ]

            input_data = {
                "messages": messages
            }

            print("\nAI Researcher is thinking...")

            print_stream(
                graph.stream(
                    input_data,
                    config=config,
                    stream_mode="values",
                )
            )

        except KeyboardInterrupt:
            print("\n\nAI Researcher stopped.")
            break

        except Exception as error:
            print(f"\nAn error occurred: {error}")
            print(
                "Check your API key, model availability, "
                "dependencies, and tool implementations."
            )
