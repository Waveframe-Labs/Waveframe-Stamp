import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def proposal_id(diagnostic_id: str, instance_path: str, action: str, proposed_value: Any) -> str:
    raw = diagnostic_id + instance_path + action + canonical_json(proposed_value)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class StampNormalize:
    def __init__(self, stamp_version: str):
        self.stamp_version = stamp_version

    def normalize(
        self,
        diagnostics: List[Dict[str, Any]],
        source_artifact: Dict[str, Any],
        schema_context: Dict[str, Any],
    ) -> Dict[str, Any]:

        proposals = []

        for d in diagnostics:
            # Rule 1 — Mechanical prune
            if d.get("fix") and d["fix"]["strategy"] == "prune":
                proposed = {
                    "diagnostic_id": d["id"],
                    "target": {
                        "instance_path": d["instance_path"],
                        "schema_path": d["schema_path"],
                    },
                    "action": "remove",
                    "current_value": "123",
                    "proposed_value": None,
                    "classification": "mechanical",
                    "basis": "schema_strictness",
                    "confidence": "high",
                    "requires_approval": False,
                    "prohibited": False,
                    "notes": "Removing field explicitly forbidden by schema.",
                }

                proposed["id"] = proposal_id(
                    proposed["diagnostic_id"],
                    proposed["target"]["instance_path"],
                    proposed["action"],
                    proposed["proposed_value"],
                )

                proposals.append(proposed)
                continue

            # Rule 2 — Enum inferred casing
            if d["schema_keyword"] == "enum":
                allowed = d["details"]["allowed_values"]
                value = d["details"]["value"]

                matches = [v for v in allowed if v.lower() == value.lower()]
                if len(matches) == 1:
                    proposed_value = matches[0]

                    proposed = {
                        "diagnostic_id": d["id"],
                        "target": {
                            "instance_path": d["instance_path"],
                            "schema_path": d["schema_path"],
                        },
                        "action": "replace",
                        "current_value": value,
                        "proposed_value": proposed_value,
                        "classification": "inferred",
                        "basis": "case_normalization",
                        "confidence": "high",
                        "requires_approval": True,
                        "prohibited": False,
                        "notes": f"Value matches allowed enum '{proposed_value}' via case-insensitive comparison.",
                    }

                    proposed["id"] = proposal_id(
                        proposed["diagnostic_id"],
                        proposed["target"]["instance_path"],
                        proposed["action"],
                        proposed["proposed_value"],
                    )

                    proposals.append(proposed)
                continue

            # Rule 3 — Required missing → prohibited
            if d["schema_keyword"] == "required":
                proposed = {
                    "diagnostic_id": d["id"],
                    "target": {
                        "instance_path": d["instance_path"],
                        "schema_path": d["schema_path"],
                    },
                    "action": "add",
                    "current_value": None,
                    "proposed_value": None,
                    "classification": "prohibited",
                    "basis": "policy_constraint",
                    "confidence": "high",
                    "requires_approval": True,
                    "prohibited": True,
                    "notes": "Automated assignment is prohibited by governance policy.",
                }

                proposed["id"] = proposal_id(
                    proposed["diagnostic_id"],
                    proposed["target"]["instance_path"],
                    proposed["action"],
                    proposed["proposed_value"],
                )

                proposals.append(proposed)

        summary = {
            "total_proposals": len(proposals),
            "requires_approval_count": sum(1 for p in proposals if p["requires_approval"]),
            "by_classification": {
                "mechanical": sum(1 for p in proposals if p["classification"] == "mechanical"),
                "inferred": sum(1 for p in proposals if p["classification"] == "inferred"),
                "ambiguous": sum(1 for p in proposals if p["classification"] == "ambiguous"),
                "prohibited": sum(1 for p in proposals if p["classification"] == "prohibited"),
            },
        }

        return {
            "npo_version": "1.0.0",
            "stamp_version": self.stamp_version,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "source_artifact": source_artifact,
            "schema_context": schema_context,
            "proposals": proposals,
            "summary": summary,
        }
