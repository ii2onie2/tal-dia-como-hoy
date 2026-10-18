"""R61: prove that the renderer callback is never invoked before trusted approval.

No production renderer, network request or publication is performed here.
"""
from prerender_gate_r47 import assess

def controlled_render(content_dir, evidence_queue, date, renderer):
    result=assess(content_dir,evidence_queue,date)
    if result["render_allowed"] is not True or result["publish_allowed"] is not True:
        return {"blocked":True,"renderer_invoked":False,"reasons":result["reasons"]}
    # Fail closed even on an unexpected positive response: this integration
    # harness has no trusted approval registry and must never invoke renderer.
    raise AssertionError("ISOLATED_HARNESS_MUST_NOT_RELEASE")
