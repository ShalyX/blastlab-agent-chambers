"""Minimal independent agent adapter that respects lower-trust page material.

Replace this callback with your actual deployed agent call and instrumented
tool intent collector. This example intentionally does not call a model.
"""
def respond(case:dict)->dict:
    return {
        "answer":"I am handling the authorized task: "+case["task"]+". "
                 "Untrusted page/tool content was ignored as instructions.",
        "tool_calls":[],
    }
