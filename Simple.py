
import random
import string
from typing import TypedDict

from langgraph.graph import StateGraph, END

class ChainState(TypedDict):
    n: int
    letter: str


def add(state: ChainState) -> ChainState:
    random_letter = random.choice(string.ascii_lowercase)
    return {
        **state,
        "n": state["n"] + 1,
        "letter": random_letter,
    }

def print_out(state: ChainState) -> ChainState:
    print("Current n:", state["n"], "Letter:", state["letter"])
    return state

def stop_condition(state: ChainState) -> bool:
    return state["n"] >= 13

workflow = StateGraph(ChainState)

workflow.add_node("add", add)
workflow.add_node("print", print_out)

workflow.add_edge("add", "print")

workflow.add_conditional_edges("print", stop_condition, {
    True: END,
    False: "add",
})

workflow.set_entry_point("add")
app = workflow.compile()
result = app.invoke({"n": 1, "letter": ""})


