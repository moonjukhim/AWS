# Env #######################################################################
#create a service client by name using the default session.
import math
import numexpr
import json
import datetime
import sys
import os

import boto3

module_path = ".."
sys.path.append(os.path.abspath(module_path))
bedrock_client = boto3.client('bedrock-runtime',region_name=os.environ.get("AWS_DEFAULT_REGION", None))
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"


#create an instance of the ChatBedrock
from langchain_aws import ChatBedrock

chat_model=ChatBedrock(
    model_id=model_id , 
    client=bedrock_client)
#invoke model
chat_model.invoke("what is AWS? Answer in a single senetence")


# ReAct #####################################################################

from langchain_core.tools import tool
@tool
def get_product_price(query:str):
    "Useful when you need to lookup product price"
    import csv
    prices = {}
    try:
        file=open('sales.csv', 'r')
    except Exception as e:
        return ("Unable to look up the price for " + query)
    reader = csv.DictReader(file)
    for row in reader:
        prices[row['product_id']] = row['price']
    file.close()
    qstr=query.split("\n")[0].strip()
    try:
            return ("Price of product "+qstr+" is "+prices.get(qstr)+"\n")
    except:
            return ("Price for product "+qstr+" is not avilable"+"\n")
    
@tool
def calculator(expression: str) -> str:
    """Use this tool to solve a math problems that involve a single line mathematical expression.
    Use math notation and not words. 
    Examples:
        "5*4" for "5 times 4"
        "5/4" for "5 divided by 4"
    """
    try:
        return str(
            numexpr.evaluate(
            expression.strip(),
            global_dict={},  
            local_dict={} # add math constants, if needed
            )
        )
    except Exception as e:
        return "Rethink your approach to this calculation"

tools = [get_product_price, calculator]

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
def output_trace(element:str, trace, node=True):
    global trace_handle
    if trace_enabled:
        print(datetime.datetime.now(),file=trace_handle)
        print(("Node: " if node else "Edge: ")+ element, file=trace_handle)
        if element == "ask_model_to_reason (entry)":
            for single_trace in trace:
                print(single_trace, file=trace_handle)
        else:
            print(trace, file=trace_handle)
        print('----', file=trace_handle)
        
def consolidate_tool_messages(message):
    tool_messages=[]
    for msg in message:
        if isinstance(msg, ToolMessage):
            tool_messages.append(msg)
    return tool_messages


## agent graph ######################################################################
from typing import Literal
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# ToolNode is a prebuilt component that runs the tool and appends the tool result to the messages 
tool_node = ToolNode(tools)

# let the model know the tools it can access
model_with_tools = chat_model.bind_tools(tools)
    
# The following function acts as the conditional edge in the graph.
# The next node could be the tools node or the end of the chain.
def next_step(state: MessagesState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        output_trace("next_step: Proceed to tools",last_message, node=False)
        return "tools"
    output_trace("next_step: Proceed to end",last_message, node=False)
    return "__end__"

#.The following node function invokes the model that has information about the available tools
def ask_model_to_reason(state: MessagesState):
    messages = state["messages"]
    output_trace("ask_model_to_reason (entry)", consolidate_tool_messages(messages))
    try:
        response = model_with_tools.invoke(messages)
    except Exception as e:
        output_trace("ask_model_to_reason", messages)
        output_trace("ask_model_to_reason", "Exception: "+str(e))
        return {"messages": [messages.append("Unable to invoke the model")]}
    output_trace("ask_model_to_reason (exit)", response)
    return {"messages": [response]}


agent_graph = StateGraph(MessagesState)

# Describe the nodes. 
# The first argument is the unique node name, and the second argument is the 
# function or object that will be called when the node is reached
agent_graph.add_node("agent", ask_model_to_reason)
agent_graph.add_node("tools", tool_node)

# Connect the entry node to the agent for the graph to start running
agent_graph.add_edge("__start__", "agent")

# Once the graph transitions to the tools node, the graph will transition to the agent node
agent_graph.add_edge("tools", "agent")

# The transition out of the agent node is conditional. 
# If the output from ask_model_to_reason function included a call to the tools, call the tool; 
# otherwise end the chain 
agent_graph.add_conditional_edges(
    "agent",
    next_step,
)

# Compile the graph definition so that it can run

react_agent = agent_graph.compile()


# visualize graph
from IPython.display import Image, display

try:
    display(Image(react_agent.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


#list of questions
questions=[]
questions.append("How much will it cost to buy 3 units of P002 and 5 units of P003?")
#questions.append("How many units of P010 can I buy with $200?")
#questions.append("Can I buy three units of P003 with $200? If not, how much more should I spend to get three units?")
#questions.append("Prices have gone up by 8%. How many units of P003 could I have purchased before the price increase with $140? How many can I buy after the price increase? Fractional units are not pssoible.")

trace_enabled=True

if trace_enabled:
    file_name="trace_"+str(datetime.datetime.now())+".txt"
    trace_handle=open(file_name, 'w')

system_message="Answer the following questions as best you can. Do not make up an answer. Think step by step. Do not perform intermediate math calculations on your own. Use the calculator tool provided for math calculations."

for q in questions:
    inputs = {"messages": [("system",system_message), ("user", q)]}
    config={"recursion_limit": 15}
    print_stream(react_agent.stream(inputs, config, stream_mode="values"))
    print("\n"+"================================ Answer complete ================================="+"\n")

if trace_enabled:
    trace_handle.close()



