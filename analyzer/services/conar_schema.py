CONAR_SCHEMA = {
    "name": "conar_image_compliance_result",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "global": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "status": {"type": "string", "enum": ["green", "yellow", "red"]},
                    "summary": {"type": "string"},
                },
                "required": ["status", "summary"],
            },
            "cards": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {"type": "string", "enum": ["conar"]},
                        "title": {"type": "string"},
                        "status": {"type": "string", "enum": ["green", "yellow", "red"]},
                        "findings": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "severity": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "what": {"type": "string"},
                                    "why": {"type": "string"},
                                    "fix": {"type": "string"},
                                },
                                "required": ["severity", "what", "why", "fix"],
                            },
                        },
                        "checks": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "has_18_plus_warning": {"type": "boolean"},
                                "has_responsible_gambling": {"type": "boolean"},
                                "mentions_easy_money": {"type": "boolean"},
                                "targets_minors": {"type": "boolean"},
                                "glamorizes_wealth": {"type": "boolean"},
                                "uses_urgency_pressure": {"type": "boolean"},
                                "minimizes_risk": {"type": "boolean"},
                            },
                            "required": [
                                "has_18_plus_warning",
                                "has_responsible_gambling",
                                "mentions_easy_money",
                                "targets_minors",
                                "glamorizes_wealth",
                                "uses_urgency_pressure",
                                "minimizes_risk",
                            ],
                        },
                    },
                    "required": ["id", "title", "status", "findings", "checks"],
                },
            },
        },
        "required": ["global", "cards"],
    },
}
