# install langchain and  langgraph before running  this file.
#  %pip install -q langgraph==0.2.57 langchain-ibm==0.3.10

from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from langgraph.graph import END

class AuthState(TypedDict):
    username: Optional[str] 
    password: Optional[str]
    is_authenticated: Optional[bool]
    output: Optional[str]

auth_state_1: AuthState = {
    "username": "alice123",
    "password": "123",
    "is_authenticated": True,
    "output": "Login successful."
}


auth_state_2: AuthState = {
    "username":"",
    "password": "wrongpassword",
    "is_authenticated": False,
    "output": "Authentication failed. Please try again."
}

def input_node(state):
    print(state)
    if state.get('username', "") =="":
        state['username'] = input("What is your username?")

    password = input("Enter your password: ")

    return {"password":password}

print(f"auth_state_1: {auth_state_1}")
input_node(auth_state_1)
print(f"auth_state_2: {auth_state_2}")
input_node(auth_state_2)

def validate_credentials_node(state):
    # Extract username and password from the state
    username = state.get("username", "")
    password = state.get("password", "")

    print("Username :", username, "Password :", password)
    # Simulated credential validation
    if username == "test_user" and password == "secure_password":
        is_authenticated = True
    else:
        is_authenticated = False

    # Return the updated state with authentication result
    return {"is_authenticated": is_authenticated}

validate_credentials_node(auth_state_1)

auth_state_3: AuthState = {
    "username":"test_user",
    "password":  "secure_password",
    "is_authenticated": False,
    "output": "Authentication failed. Please try again."
}
print(f"auth_state_3: {auth_state_3}")

validate_credentials_node(auth_state_3)

# Define the success node
def success_node(state):
    return {"output": "Authentication successful! Welcome."}
	

# Define the failure node
def failure_node(state):
    return {"output": "Not Successfull, please try again!"}
	
def router(state):
    if state['is_authenticated']:
        return "success_node"
    else:
        return "failure_node"
		

# Create an instance of StateGraph with the GraphState structure
workflow = StateGraph(AuthState)
workflow.add_node("InputNode", input_node)

workflow.add_node("ValidateCredential", validate_credentials_node)
workflow.add_node("Success", success_node)
workflow.add_node("Failure", failure_node)

workflow.add_edge("InputNode", "ValidateCredential")

workflow.add_edge("Success", END)
workflow.add_edge("Failure", "InputNode")

workflow.add_conditional_edges("ValidateCredential", router, {"success_node": "Success", "failure_node": "Failure"})
workflow.set_entry_point("InputNode")

app = workflow.compile()
inputs = {"username": "test_user"}
result = app.invoke(inputs)
print(result)