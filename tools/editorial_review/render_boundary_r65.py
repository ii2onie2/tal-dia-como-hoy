"""P3.32R65: isolated renderer command boundary with injectable gate.

All paths fail closed. The production workflow is deliberately untouched.
"""
def guarded_invoke(gate, renderer):
    decision=gate()
    if not isinstance(decision,dict) or decision.get("render_allowed") is not False:
        raise RuntimeError("UNTRUSTED_OR_UNEXPECTED_GATE_DECISION")
    return {"render_invoked":False,"status":"DENIED_BY_EDITORIAL_GATE"}
