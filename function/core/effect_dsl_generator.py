# coding: utf-8
"""Prototype DSL generator for Yu-Gi-Oh! card effects.

This module provides :func:`generate_effect_yaml` which converts official
English card effect text into a YAML formatted DSL (schema v3).
"""

import re
from typing import List, Dict, Any


def split_effects(text: str) -> List[str]:
    """Split raw effect text into individual effect segments."""
    # Markers like "①", "②" are used to denote separate effects.
    markers = "①②③④⑤⑥⑦⑧⑨⑩"
    pattern = f"[{markers}]"
    parts: List[str] = []
    indexes = [m.start() for m in re.finditer(pattern, text)]
    if indexes:
        indexes.append(len(text))
        for i in range(len(indexes) - 1):
            start = indexes[i] + 1
            end = indexes[i + 1]
            part = text[start:end].strip()
            if part:
                parts.append(part)
    else:
        # Fallback: split by sentences
        sentences = re.split(r"\.(?=\s*[A-Z])", text)
        for sen in sentences:
            sen = sen.strip()
            if sen:
                parts.append(sen)
    return parts


# Simple regex pattern dictionaries
TRIGGER_PATTERNS = {
    r"when this card is normal summoned": "on_normal_summon",
    r"when this card is special summoned": "on_special_summon",
    r"when this card is sent to the gy": "on_sent_to_graveyard",
    r"if this card is in your gy": "on_in_graveyard",
}

CONDITION_PATTERNS = {
    r"in your gy": 'self.location == "graveyard"',
    r"control no monsters": 'self.controller.monsters == 0',
}

COST_PATTERNS = [
    (r"pay (\d+) lp", lambda m: f"lose_life({m.group(1)})"),
    (r"discard (\d+) card", lambda m: f"discard({m.group(1)})"),
    (r"banish (\d+) card", lambda m: f"banish({m.group(1)})"),
]

ACTION_PATTERNS = [
    (r"draw (\d+) card", lambda m: f"draw({m.group(1)})"),
    (r"special summon", lambda m: 'special_summon(self, to="field", position="defense")'),
    (r"add .* to your hand", lambda m: 'add_to_hand(target)'),
]


def extract_first(pattern_dict: Dict[str, str], text: str) -> str:
    for pattern, value in pattern_dict.items():
        if re.search(pattern, text, re.IGNORECASE):
            return value
    return ""


def extract_list(patterns: List, text: str) -> List[str]:
    results = []
    for pat, func in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            results.append(func(m))
    return results


def parse_segment(segment: str, cid: str, index: int) -> Dict[str, Any]:
    effect_id = f"{cid}_{index}"

    optional = bool(re.search(r"you can", segment, re.IGNORECASE))
    timing_type = "when" if re.search(r"\bwhen\b", segment, re.IGNORECASE) else "if"
    trigger = extract_first(TRIGGER_PATTERNS, segment)

    cost_text = ""
    action_text = segment
    if ";" in segment:
        cost_text, action_text = segment.split(";", 1)
    elif ":" in segment:
        condition_part, action_text = segment.split(":", 1)
        cost_text = condition_part
    
    condition = extract_first(CONDITION_PATTERNS, cost_text)
    costs = extract_list(COST_PATTERNS, cost_text)
    actions = extract_list(ACTION_PATTERNS, action_text)

    return {
        "id": effect_id,
        "trigger": trigger,
        "timing_type": timing_type,
        "optional": optional,
        "restriction": {"limit_per_turn": 1, "group": f"{cid}_group"},
        "target": [],
        "condition": condition,
        "cost": costs,
        "action": actions,
    }


def dict_to_yaml(data: Dict[str, Any], indent: int = 0) -> List[str]:
    lines = []
    pad = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            lines.extend(dict_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            if not value:
                lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}:")
                for item in value:
                    if isinstance(item, (dict, list)):
                        lines.append(f"{pad}  -")
                        lines.extend(dict_to_yaml(item, indent + 2))
                    else:
                        lines.append(f"{pad}  - {item}")
        else:
            if isinstance(value, str):
                import json
                value_str = json.dumps(value)
            elif isinstance(value, bool):
                value_str = "true" if value else "false"
            else:
                value_str = str(value)
            lines.append(f"{pad}{key}: {value_str}")
    return lines


def generate_effect_yaml(cid: str, name: str, text: str) -> str:
    effects_raw = split_effects(text)
    effects = [parse_segment(seg, cid, i + 1) for i, seg in enumerate(effects_raw)]
    card_dict = {"cid": cid, "name": name, "effects": effects}
    yaml_lines = dict_to_yaml(card_dict)
    return "\n".join(yaml_lines) + "\n"


__all__ = ["generate_effect_yaml"]
