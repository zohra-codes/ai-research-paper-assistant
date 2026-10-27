#step1: Install & import dependencies
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from arxiv_tool import arxiv_search
from read_pdf import read_pdf
from write_pdf import render_latex_pdf
import os
from dotenv import load_dotenv

load_dotenv()

#stp2: Setup LLM and tools
tools = [arxiv_search, read_pdf, render_latex_pdf]
model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)
#step3: Run the agent with an initial prompt
graph = create_agent(model, tools=tools)
INITIAL_PROMPT = """
You are an expert researcher in the fields of physics, mathematics,
computer science, quantitative biology, quantitative finance, statistics,
electrical engineering and systems science, and economics.

You are going to analyze recent research papers in one of these fields in
order to identify promising new research directions and then write a new
research paper. For research information or getting papers, ALWAYS use arxiv.org.
You will use the tools provided to search for papers, read them, and write a new
paper based on the ideas you find.

To start with, have a conversation with me in order to figure out what topic
to research. Then tell me about some recently published papers with that topic.
Once I've decided which paper I'm interested in, go ahead and read it in order
to understand the research that was done and the outcomes.

Pay particular attention to the ideas for future research and think carefully
about them, then come up with a few ideas. Let me know what they are and I'll
decide what one you should write a paper about.

Finally, I'll ask you to go ahead and write the paper. Make sure that you
include mathematical equations in the paper. Once it's complete, you should
render it as a LaTeX PDF. When you give papers references, always attatch the pdf links to the paper"""


while True:
    user_input = input("User: ")

    if user_input.strip():
        messages = [
            {"role": "system", "content": INITIAL_PROMPT},
            {"role": "user", "content": user_input}
        ]

        input_data = {
            "messages": messages
        }

        for event in graph.stream(input_data, stream_mode="values"):
            if event.get("messages"):
                last_message = event["messages"][-1]

                if last_message.type == "ai":
                    print("AI:", last_message.content)
