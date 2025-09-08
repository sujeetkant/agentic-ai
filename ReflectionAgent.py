# this example uses a reflction agent.
# It starts with a linkedin in post and it improves post content iteratively.
# It runs for 6 iterations.
# Basically, it makes the output more and more verbose.


from langchain_ibm import ChatWatsonx
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph, StateGraph
from langgraph.graph import MessageGraph
from IPython.display import Image, display

from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# IGNORE IF YOU ARE NOT RUNNING LOCALLY
#from langchain_ibm import ChatWatsonx
#watsonx_llm = ChatWatsonx(
#    model_id="ibm/granite-3-2-8b-instruct",
#    url="https://us-south.ml.cloud.ibm.com",
#    project_id="your project id associated with the API key",
#    api_key="your watsonx.ai api key here",
#)

llm = ChatWatsonx(
    model_id="ibm/granite-3-3-8b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="skills-network"
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a professional LinkedIn content assistant tasked with crafting engaging, insightful, and well-structured LinkedIn posts."
            " Generate the best LinkedIn post possible for the user's request."
            " If the user provides feedback or critique, respond with a refined version of your previous attempts, improving clarity, tone, or engagement as needed.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


generate_chain = generation_prompt | llm


reflection_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a professional LinkedIn content strategist and thought leadership expert. Your task is to critically evaluate the given LinkedIn post and provide a comprehensive critique. Follow these guidelines:

        1. Assess the post’s overall quality, professionalism, and alignment with LinkedIn best practices.
        2. Evaluate the structure, tone, clarity, and readability of the post.
        3. Analyze the post’s potential for engagement (likes, comments, shares) and its effectiveness in building professional credibility.
        4. Consider the post’s relevance to the author’s industry, audience, or current trends.
        5. Examine the use of formatting (e.g., line breaks, bullet points), hashtags, mentions, and media (if any).
        6. Evaluate the effectiveness of any call-to-action or takeaway.

        Provide a detailed critique that includes:
        - A brief explanation of the post’s strengths and weaknesses.
        - Specific areas that could be improved.
        - Actionable suggestions for enhancing clarity, engagement, and professionalism.

        Your critique will be used to improve the post in the next revision step, so ensure your feedback is thoughtful, constructive, and practical.
        """
    ),
    MessagesPlaceholder(variable_name="messages")
])

reflect_chain = reflection_prompt | llm

def generation_node(state: Sequence[BaseMessage]) -> List[BaseMessage]:
    generated_post = generate_chain.invoke({"messages": state})
    return [AIMessage(content=generated_post.content)]

def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    res = reflect_chain.invoke({"messages": messages})  # Passes messages as input to reflect_chain
    return [HumanMessage(content=res.content)]  # Returns the refined message as HumanMessage for feedback

def should_continue(state: List[BaseMessage]):
    print(state)
    print(len(state))
    print("----------------------------------------------------------------------")
    if len(state) > 6:
        return END
    return "reflect"

graph = MessageGraph()
graph.add_node("generate", generation_node)
graph.add_node("reflect", reflection_node)
graph.add_edge("reflect", "generate")
graph.set_entry_point("generate")
graph.add_conditional_edges("generate", should_continue)

workflow = graph.compile()
inputs = HumanMessage(content="""Write a linkedin post on getting a software developer job at IBM under 160 characters""")
response = workflow.invoke(inputs)

response[1].content
response[2].content
response[-1].content




