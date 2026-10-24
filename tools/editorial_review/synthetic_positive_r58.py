"""P3.32R58 synthetic-only positive contract path, with terminal release denial."""
import hashlib
import hmac
from datetime import datetime,timezone
from approval_contract_r48 import canonical
from approval_replay_r49 import assess

def synthetic_walkthrough():
    key=b"synthetic-offline-approval-key-material-00000000000"
    digest=hashlib.sha256(b"fully synthetic historical fixture").hexdigest()
    p={"dossier_id":"SYNTHETIC-ONLY","content_sha256":digest,
       "editor_id":"synthetic-reviewer","decision":"APPROVED",
       "timestamp":"2026-10-18T12:00:00Z","source_review":True,"media_rights":True}
    record={"payload":p,"signature":hmac.new(key,canonical(p),hashlib.sha256).hexdigest()}
    result=assess(record,key,digest,set(),{"synthetic-reviewer"},datetime(2026,10,18,12,0,tzinfo=timezone.utc))
    return {"contract_result":result,"synthetic":True,"editorial_approved":False,
            "render_authorized":False,"transfer_authorized":False,"publish_authorized":False}
