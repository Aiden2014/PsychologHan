#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Psycholog text and game-flow context from decompiled code and UABEA dumps."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional


SOURCE_RE = re.compile(
    r"-(?P<source>resources\.assets|sharedassets\d+\.assets|"
    r"globalgamemanagers(?:\.assets)?|level\d+)-(?P<path_id>\d+)"
    r"\.(?P<extension>[^.]+)$",
    re.IGNORECASE,
)
MAX_TRANSLATION_KEY_LENGTH = 512
KNOWN_SPEAKER_WRAPPERS = {
    "vera", "joe", "deborah", "jaden", "ashley", "boss", "josh", "shannon",
    "jackson", "tanaka", "mike", "passenger", "raymond", "green",
    "killerWithGlasses", "killerRevealed", "killerRaymond", "bennett", "nurse",
    "nurseGlad", "jennifer", "emily", "boy", "girl", "clerk",
}
OPTION_WRAPPERS = {"warm", "joking", "analytical", "stern", "silent"}
USER_TEXT_FIELDS = {
    "trustComment", "treatmentComment", "rune", "journalText", "messageText",
}


@dataclass(frozen=True)
class Invocation:
    name: str
    arguments: str
    start: int
    end: int
    line: int


@dataclass
class DialogueRow:
    node_id: Optional[int]
    speaker: str
    text: str
    to_id: Optional[int]
    source_line: int
    source: str = "GameManager.cs"


@dataclass
class ChoiceRow:
    from_id: Optional[int]
    option_id: Optional[int]
    text: str
    to_id: Optional[int]
    source_line: int
    source: str = "GameManager.cs"


@dataclass
class TextRow:
    category: str
    key_suffix: str
    text: str
    source_line: int = 0
    source: str = ""
    detail: str = ""


@dataclass
class FlowEvent:
    node_id: Optional[int]
    event_type: str
    details: str
    source_line: int
    parent_call: str = ""


@dataclass
class GameData:
    dialogues: list[DialogueRow] = field(default_factory=list)
    choices: list[ChoiceRow] = field(default_factory=list)
    items: list[TextRow] = field(default_factory=list)
    flow_events: list[FlowEvent] = field(default_factory=list)
    character_names: set[str] = field(default_factory=set)
    client_info: list[TextRow] = field(default_factory=list)
    ending: list[TextRow] = field(default_factory=list)
    ui: list[TextRow] = field(default_factory=list)


@dataclass(frozen=True)
class CsvRow:
    key: str
    original: str
    translated: str = ""


@dataclass
class ExtractionStats:
    dialogue_count: int = 0
    choice_count: int = 0
    item_count: int = 0
    character_name_count: int = 0
    client_info_count: int = 0
    ending_count: int = 0
    ui_count: int = 0
    flow_count: int = 0
    asset_count: int = 0
    unresolved_count: int = 0


@dataclass(frozen=True)
class UnityRef:
    file_id: int
    path_id: int


@dataclass
class ResourceObject:
    source: str
    path_id: int
    type_name: str
    name: str
    path: Path
    data: dict[str, Any] = field(default_factory=dict)


def _skip_comment(text: str, index: int) -> int:
    if text.startswith("//", index):
        end = text.find("\n", index + 2)
        return len(text) if end < 0 else end
    if text.startswith("/*", index):
        end = text.find("*/", index + 2)
        return len(text) if end < 0 else end + 2
    return index


def _matching_paren(text: str, opening: int) -> int:
    depth = 1
    index = opening + 1
    while index < len(text):
        if text.startswith("//", index) or text.startswith("/*", index):
            index = _skip_comment(text, index)
            continue
        if text[index] in ('"', "'") or text.startswith('@"', index):
            index = _skip_string(text, index)
            continue
        if text[index] == '(':
            depth += 1
        elif text[index] == ')':
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _matching_brace(text: str, opening: int) -> int:
    depth = 1
    index = opening + 1
    while index < len(text):
        if text.startswith("//", index) or text.startswith("/*", index):
            index = _skip_comment(text, index)
            continue
        if text[index] in ('"', "'") or text.startswith('@"', index):
            index = _skip_string(text, index)
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(text) - 1


def _skip_string(text: str, index: int) -> int:
    """Skip a C# normal, verbatim, or character literal."""
    verbatim = text.startswith('@"', index)
    if verbatim:
        index += 2
    else:
        quote = text[index]
        index += 1
    while index < len(text):
        if verbatim:
            if text.startswith('""', index):
                index += 2
                continue
            if text[index] == '"':
                return index + 1
        elif text[index] == "\\":
            index += 2
            continue
        elif text[index] == quote:
            return index + 1
        index += 1
    return len(text)
    quote = text[index]
    index += 1
    while index < len(text):
        if text[index] == "\\":
            index += 2
        elif text[index] == quote:
            return index + 1
        else:
            index += 1
    return len(text)


def scan_invocations(source: str, names: set[str]) -> list[Invocation]:
    """Find calls with balanced parentheses while ignoring comments and strings."""
    if not names:
        return []
    pattern = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(
        re.escape(name) for name in sorted(names, key=len, reverse=True)
    ) + r")(?![A-Za-z0-9_])")
    calls: list[Invocation] = []
    index = 0
    while index < len(source):
        if source.startswith("//", index) or source.startswith("/*", index):
            index = _skip_comment(source, index)
            continue
        if source[index] in ('"', "'") or source.startswith('@"', index):
            index = _skip_string(source, index)
            continue
        match = pattern.match(source, index)
        if not match:
            index += 1
            continue
        name = match.group(1)
        cursor = match.end()
        while cursor < len(source) and source[cursor].isspace():
            cursor += 1
        if cursor >= len(source) or source[cursor] != '(':
            index = match.end()
            continue
        closing = _matching_paren(source, cursor)
        calls.append(Invocation(
            name=name,
            arguments=source[cursor + 1:closing],
            start=match.start(),
            end=closing + 1,
            line=source.count("\n", 0, match.start()) + 1,
        ))
        # Continue scanning inside the argument list as well.  Story calls
        # commonly contain delegates with nested sound/cutscene calls.
        index = match.end()
    return calls


def split_top_level_args(text: str) -> list[str]:
    """Split a call argument list without splitting nested delegates or strings."""
    result: list[str] = []
    start = 0
    parens = braces = brackets = 0
    index = 0
    while index < len(text):
        if text.startswith("//", index) or text.startswith("/*", index):
            index = _skip_comment(text, index)
            continue
        if text[index] in ('"', "'") or text.startswith('@"', index):
            index = _skip_string(text, index)
            continue
        char = text[index]
        if char == '(':
            parens += 1
        elif char == ')':
            parens -= 1
        elif char == '{':
            braces += 1
        elif char == '}':
            braces -= 1
        elif char == '[':
            brackets += 1
        elif char == ']':
            brackets -= 1
        elif char == ',' and parens == braces == brackets == 0:
            result.append(text[start:index].strip())
            start = index + 1
        index += 1
    tail = text[start:].strip()
    if tail or result:
        result.append(tail)
    return result


def _split_top_level_plus(text: str) -> list[str]:
    result: list[str] = []
    start = 0
    parens = braces = brackets = 0
    index = 0
    while index < len(text):
        if text[index] in ('"', "'") or text.startswith('@"', index):
            index = _skip_string(text, index)
            continue
        char = text[index]
        if char == '(':
            parens += 1
        elif char == ')':
            parens -= 1
        elif char == '{':
            braces += 1
        elif char == '}':
            braces -= 1
        elif char == '[':
            brackets += 1
        elif char == ']':
            brackets -= 1
        elif char == '+' and parens == braces == brackets == 0:
            result.append(text[start:index].strip())
            start = index + 1
        index += 1
    result.append(text[start:].strip())
    return result


def decode_csharp_string(token: str) -> str:
    token = token.strip()
    if len(token) < 2:
        return token
    if token.startswith('@"') and token.endswith('"'):
        return token[2:-1].replace('""', '"')
    if token[0] != '"' or token[-1] != '"':
        return token
    body = token[1:-1]
    result: list[str] = []
    index = 0
    escapes = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "\\": "\\", '"': '"', "'": "'"}
    while index < len(body):
        if body[index] != "\\" or index + 1 >= len(body):
            result.append(body[index])
            index += 1
            continue
        code = body[index + 1]
        if code in escapes:
            result.append(escapes[code])
            index += 2
        elif code == "u" and index + 5 < len(body):
            result.append(chr(int(body[index + 2:index + 6], 16)))
            index += 6
        elif code == "x":
            match = re.match(r"x([0-9A-Fa-f]{1,4})", body[index + 1:])
            if match:
                result.append(chr(int(match.group(1), 16)))
                index += 1 + len(match.group(0))
            else:
                result.append(code)
                index += 2
        else:
            result.append(code)
            index += 2
    return "".join(result)


def _is_string_literal(expression: str) -> bool:
    expression = expression.strip()
    return (expression.startswith('"') and expression.endswith('"')) or (
        expression.startswith('@"') and expression.endswith('"')
    )


def literal_text(expression: str) -> tuple[Optional[str], str]:
    """Return visible literal pieces and preserve non-literal expressions as placeholders."""
    expression = expression.strip()
    if _is_string_literal(expression):
        return decode_csharp_string(expression), ""
    parts = _split_top_level_plus(expression)
    if len(parts) == 1:
        return None, expression
    pieces: list[str] = []
    expressions: list[str] = []
    for part in parts:
        if _is_string_literal(part):
            pieces.append(decode_csharp_string(part))
        elif part:
            placeholder = "{EXPR_%d}" % (len(expressions) + 1)
            pieces.append(placeholder)
            expressions.append(part)
    return "".join(pieces), " + ".join(expressions)


def _integer(expression: str) -> Optional[int]:
    match = re.search(r"[-+]?\d+", expression.strip())
    return int(match.group(0)) if match else None


def _float_value(expression: str) -> str:
    return expression.strip().rstrip("fF")


def _looks_like_declaration(source: str, call: Invocation) -> bool:
    line_start = source.rfind("\n", 0, call.start) + 1
    prefix = source[line_start:call.start]
    return bool(re.search(r"\b(?:public|private|protected|internal)\b.*\b(?:void|int|float|string|bool)\s+$", prefix))


def _method_wrapper_names(source: str) -> dict[str, str]:
    wrappers: dict[str, str] = {}
    pattern = re.compile(
        r"public\s+void\s+(\w+)\s*\(\s*int\s+id\s*,\s*string\s+text\s*,\s*int\s+toId[^)]*\)\s*\{([^{}]*)\}",
        re.DOTALL,
    )
    for match in pattern.finditer(source):
        name, body = match.groups()
        speaker = re.search(r'addSpeaker\s*\(\s*id\s*,\s*(["@][^,]+),', body)
        if speaker:
            wrappers[name] = decode_csharp_string(speaker.group(1).strip())
        elif name == "addMe":
            wrappers[name] = "ME"
    return wrappers


def _story_method_ranges(source: str) -> list[tuple[str, int, int, int, int]]:
    """Return story method name, source span, and start/end line numbers."""
    pattern = re.compile(
        r"\b(?:public|private|protected|internal)\s+(?:void|IEnumerator)\s+"
        r"(?P<name>story\w+)\s*\([^)]*\)\s*\{"
    )
    ranges: list[tuple[str, int, int, int, int]] = []
    for match in pattern.finditer(source):
        opening = source.find("{", match.start(), match.end())
        closing = _matching_brace(source, opening)
        ranges.append((
            match.group("name"),
            match.start(),
            closing + 1,
            source.count("\n", 0, match.start()) + 1,
            source.count("\n", 0, closing) + 1,
        ))
    return ranges


def _story_method_for_position(
    position: int,
    ranges: list[tuple[str, int, int, int, int]],
) -> Optional[tuple[str, int, int, int, int]]:
    matches = [item for item in ranges if item[1] <= position < item[2]]
    return min(matches, key=lambda item: item[2] - item[1], default=None)


def _story_flow_events(
    source: str,
    calls: list[Invocation],
    wrappers: dict[str, str],
    ranges: list[tuple[str, int, int, int, int]],
) -> list[FlowEvent]:
    events: list[FlowEvent] = []
    for name, _, _, start_line, end_line in ranges:
        events.append(FlowEvent(
            None,
            "story_module",
            f"module={name}; start={start_line}; end={end_line}",
            start_line,
        ))
    for call in calls:
        method = _story_method_for_position(call.start, ranges)
        if not method:
            continue
        module = method[0]
        args = split_top_level_args(call.arguments)
        if (call.name in wrappers or call.name in KNOWN_SPEAKER_WRAPPERS) and len(args) >= 3:
            node = _integer(args[0])
            speaker = wrappers.get(call.name, call.name.upper())
            events.append(FlowEvent(
                node,
                "dialogue_edge",
                f"module={module}; speaker={speaker}; to={_integer(args[2])}",
                call.line,
            ))
        elif call.name == "addSpeaker" and len(args) >= 4:
            events.append(FlowEvent(
                _integer(args[0]),
                "dialogue_edge",
                f"module={module}; speaker={decode_csharp_string(args[1])}; to={_integer(args[3])}",
                call.line,
            ))
        elif (call.name in OPTION_WRAPPERS or call.name == "addOpt") and len(args) >= 4:
            events.append(FlowEvent(
                _integer(args[0]),
                "choice_edge",
                f"module={module}; option={_integer(args[1])}; to={_integer(args[3])}",
                call.line,
            ))
    return events


def _containing_call(call: Invocation, calls: list[Invocation]) -> Optional[Invocation]:
    parents = [candidate for candidate in calls if candidate.start < call.start and call.end <= candidate.end]
    return min(parents, key=lambda item: item.end - item.start, default=None)


def _scan_text_assignments(
    source: str,
    target_pattern: str = r"[A-Za-z_][\w.\[\]]*\.text",
) -> Iterable[tuple[int, str, str]]:
    pattern = re.compile(
        rf"(?P<target>{target_pattern})\s*=\s*(?P<expression>[^;]+);"
    )
    for match in pattern.finditer(source):
        yield source.count("\n", 0, match.start()) + 1, match.group("target"), match.group("expression").strip()


def _parse_state_texts(path: Path) -> tuple[list[TextRow], list[TextRow]]:
    client_info: list[TextRow] = []
    ending: list[TextRow] = []
    if not path.exists():
        return client_info, ending
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r'public\s+string\s+(\w+)\s*=\s*'
        r'(?P<literal>@"(?:""|[^"])*"|"(?:\\.|[^"\\])*")\s*;'
    )
    for match in pattern.finditer(text):
        field_name = match.group(1)
        original = decode_csharp_string(match.group("literal"))
        if field_name.startswith(("trustComment", "treatmentComment")):
            client_info.append(TextRow("client_info", field_name, original, text.count("\n", 0, match.start()) + 1, path.name))
        elif field_name.startswith("rune"):
            ending.append(TextRow("ending", field_name, original, text.count("\n", 0, match.start()) + 1, path.name))
    return client_info, ending


def _parse_death_runes(path: Path) -> list[TextRow]:
    if not path.exists():
        return []
    rows: list[TextRow] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for line_no, target, expression in _scan_text_assignments(text):
        if not target.startswith("rune"):
            continue
        value, detail = literal_text(expression)
        if value:
            rows.append(TextRow("ending", f"{target}|||{line_no}", value, line_no, path.name, detail))
    return rows


def _parse_audio_aliases(path: Path) -> dict[str, str]:
    """Read strToAudio switch aliases such as subway -> subwayAmbience."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(r'case\s+"([^"]+)"\s*:\s*return\s+([A-Za-z_]\w*)\s*;')
    return {match.group(1): match.group(2) for match in pattern.finditer(text)}


def parse_game_manager(path: Path) -> GameData:
    source = path.read_text(encoding="utf-8", errors="replace")
    data = GameData()
    wrappers = _method_wrapper_names(source)
    wrappers.setdefault("addMe", "ME")
    data.character_names.update(name for name in wrappers.values() if name != "ME")
    story_ranges = _story_method_ranges(source)

    names = set(wrappers) | KNOWN_SPEAKER_WRAPPERS | OPTION_WRAPPERS | {
        "addMe", "addSpeaker", "addOpt", "illustrate", "animate", "addCutscene",
        "addMusic", "addAmbience", "playSoundEffect", "addChoice", "addMap", "addPac",
        "applyTransition", "addEmoji", "addTransition", "fight", "died", "failed",
    }
    calls = [call for call in scan_invocations(source, names) if not _looks_like_declaration(source, call)]

    for call in sorted(calls, key=lambda item: item.start):
        args = split_top_level_args(call.arguments)
        if (call.name in wrappers or call.name in KNOWN_SPEAKER_WRAPPERS) and len(args) >= 3:
            node_id = _integer(args[0])
            text, detail = literal_text(args[1])
            to_id = _integer(args[2])
            if text:
                speaker = wrappers.get(call.name, call.name.upper())
                data.dialogues.append(DialogueRow(node_id, speaker, text, to_id, call.line))
                data.character_names.add(speaker)
                if detail:
                    data.flow_events.append(FlowEvent(node_id, "dynamic_text", f"text={text}; expression={detail}", call.line, call.name))
            continue
        if call.name == "addSpeaker" and len(args) >= 4:
            node_id = _integer(args[0])
            speaker = decode_csharp_string(args[1])
            text, detail = literal_text(args[2])
            if text:
                data.dialogues.append(DialogueRow(node_id, speaker, text, _integer(args[3]), call.line))
                data.character_names.add(speaker)
                if detail:
                    data.flow_events.append(FlowEvent(node_id, "dynamic_text", f"text={text}; expression={detail}", call.line, call.name))
            continue
        if call.name in OPTION_WRAPPERS or call.name == "addOpt":
            if len(args) >= 4:
                from_id, option_id, text, to_id = _integer(args[0]), _integer(args[1]), literal_text(args[2])[0], _integer(args[3])
                if text:
                    data.choices.append(ChoiceRow(from_id, option_id, text, to_id, call.line))
            continue
        if call.name == "fight" and len(args) >= 2:
            node_id = _integer(args[0])
            text, _ = literal_text(args[1])
            if text:
                data.dialogues.append(DialogueRow(node_id, "ME", text, 111000, call.line))
            data.choices.append(ChoiceRow(node_id, (node_id or 0) * 100000, "Fight.", 111000, call.line))
            continue
        if call.name in {"died", "failed"} and len(args) >= 2:
            node_id = _integer(args[0])
            text, detail = literal_text(args[1])
            suffix = "Your mission has failed." if call.name == "failed" else "You have died. Your mission has failed."
            if text:
                data.dialogues.append(DialogueRow(node_id, "ME", text + "\n\n" + suffix, 1000, call.line))
            data.flow_events.append(FlowEvent(node_id, "system_text", f"{suffix}; trigger={call.name}", call.line, call.name))
            continue
        if call.name == "illustrate" and len(args) >= 2:
            data.flow_events.append(FlowEvent(_integer(args[0]), "image", f"image={decode_csharp_string(args[1])}", call.line))
        elif call.name == "animate" and len(args) >= 2:
            data.flow_events.append(FlowEvent(_integer(args[0]), "animated_background", f"name={decode_csharp_string(args[1])}", call.line))
        elif call.name == "addCutscene" and len(args) >= 3:
            data.flow_events.append(FlowEvent(_integer(args[0]), "cutscene", f"name={decode_csharp_string(args[1])}; next={_integer(args[2])}", call.line))
        elif call.name in {"addMusic", "addAmbience"} and len(args) >= 2:
            level = _float_value(args[2]) if len(args) >= 3 else "1"
            data.flow_events.append(FlowEvent(_integer(args[0]), call.name[3:].lower(), f"name={decode_csharp_string(args[1])}; volume={level}", call.line))
        elif call.name == "playSoundEffect" and args:
            parent = _containing_call(call, calls)
            volume = _float_value(args[1]) if len(args) >= 2 else "1"
            node = _integer(split_top_level_args(parent.arguments)[0]) if parent and split_top_level_args(parent.arguments) else None
            data.flow_events.append(FlowEvent(node, "sound", f"source={args[0].strip()}; volume={volume}", call.line, parent.name if parent else ""))
        elif call.name in {"addChoice", "addMap", "addPac"} and args:
            data.flow_events.append(FlowEvent(_integer(args[0]), call.name[3:].lower(), "", call.line))
        elif call.name == "applyTransition" and len(args) >= 4:
            data.flow_events.append(FlowEvent(_integer(args[0]), "transition", f"option={args[1].strip()}; id={decode_csharp_string(args[2])}; next={_integer(args[3])}", call.line))
        elif call.name == "addEmoji" and len(args) >= 2:
            data.flow_events.append(FlowEvent(None, "option_emoji", f"option={args[0].strip()}; emoji={decode_csharp_string(args[1])}", call.line))
        elif call.name == "addTransition" and len(args) >= 10:
            data.flow_events.append(FlowEvent(None, "transition_definition", f"id={decode_csharp_string(args[0])}; type={decode_csharp_string(args[9])}", call.line))

    for line_no, target, expression in _scan_text_assignments(source):
        value, detail = literal_text(expression)
        if not value:
            continue
        if target.startswith("gS.trustComment") or target.startswith("gS.treatmentComment"):
            data.client_info.append(TextRow("client_info", f"{target}|||{line_no}", value, line_no, path.name, detail))
        elif target.startswith("sitItems["):
            match = re.search(r"sitItems\[(\d+)\]", target)
            node_id = int(match.group(1)) if match else None
            item_id = match.group(1) if match else target
            data.items.append(TextRow("item", f"{item_id}|||{line_no}", value, line_no, path.name, detail))
            data.flow_events.append(FlowEvent(node_id, "dynamic_text", f"target={target}; text={value}; expression={detail}", line_no))
        elif target.startswith("optionItems["):
            data.choices.append(ChoiceRow(None, _integer(target), value, None, line_no, path.name))
        elif target != "meText" and target != "speakerText":
            data.ui.append(TextRow("ui", f"{target}|||{line_no}", value, line_no, path.name, detail))

    for line_no, target, expression in _scan_text_assignments(
        source,
        r"gS\.(?:trustComment|treatmentComment)\w+",
    ):
        value, detail = literal_text(expression)
        if value:
            data.client_info.append(TextRow("client_info", f"{target}|||{line_no}", value, line_no, path.name, detail))

    state_client, state_ending = _parse_state_texts(path.with_name("GameState.cs"))
    data.client_info.extend(state_client)
    data.ending.extend(state_ending)
    data.ending.extend(_parse_death_runes(path.with_name("DeathRunes.cs")))
    data.flow_events.extend(_story_flow_events(source, calls, wrappers, story_ranges))
    return data


class ResourceIndex:
    def __init__(self, root: Path):
        self.root = root
        self.objects: list[ResourceObject] = []
        self.by_key: dict[tuple[str, int], list[ResourceObject]] = {}
        self.by_type_path: dict[tuple[str, int], list[ResourceObject]] = {}
        self.unresolved: list[str] = []

    @classmethod
    def from_root(cls, root: Path) -> "ResourceIndex":
        index = cls(root)
        if not root.exists():
            return index
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".json", ".png", ".ogg", ".wav", ".mp3"}:
                continue
            match = SOURCE_RE.search(path.name)
            if not match:
                continue
            source = match.group("source")
            path_id = int(match.group("path_id"))
            declared_type = path.parent.name
            data: dict[str, Any] = {}
            filename_name = path.name[:match.start()].strip()
            name = filename_name
            if path.suffix.lower() == ".json":
                try:
                    loaded = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        data = loaded
                    name = str(loaded.get("m_Name") or name).strip()
                except (OSError, json.JSONDecodeError):
                    continue
                if declared_type == "MonoBehaviour":
                    declared_type = filename_name.split("-")[0] if filename_name else "MonoBehaviour"
            else:
                name = name.strip()
            obj = ResourceObject(source, path_id, declared_type, name, path, data)
            index.objects.append(obj)
            index.by_key.setdefault((source, path_id), []).append(obj)
            index.by_type_path.setdefault((declared_type, path_id), []).append(obj)
        return index

    def find_by_path_id(self, source: str, path_id: int, type_name: Optional[str] = None) -> Optional[ResourceObject]:
        candidates = self.by_key.get((source, path_id), [])
        if type_name:
            candidates = [candidate for candidate in candidates if candidate.type_name == type_name]
        return candidates[0] if len(candidates) == 1 else (candidates[0] if candidates else None)

    def resolve(self, reference: dict[str, Any], owner: ResourceObject, expected_types: Optional[set[str]] = None) -> Optional[ResourceObject]:
        if not isinstance(reference, dict):
            return None
        path_id = int(reference.get("m_PathID", 0) or 0)
        file_id = int(reference.get("m_FileID", 0) or 0)
        if path_id == 0:
            return None
        local = self.by_key.get((owner.source, path_id), []) if file_id == 0 else []
        candidates = local or [candidate for candidate in self.objects if candidate.path_id == path_id]
        if expected_types:
            candidates = [candidate for candidate in candidates if candidate.type_name in expected_types]
        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            self.unresolved.append(f"owner={owner.path.name}; ref={file_id}:{path_id}; expected={sorted(expected_types or set())}")
        else:
            self.unresolved.append(f"ambiguous owner={owner.path.name}; ref={file_id}:{path_id}; candidates={len(candidates)}")
        return None

    def find_named(self, type_name: str, name: str) -> Optional[ResourceObject]:
        matches = [obj for obj in self.objects if obj.type_name == type_name and obj.name == name]
        return matches[0] if len(matches) == 1 else (matches[0] if matches else None)

    def resolve_audio_field(self, field_name: str) -> Optional[ResourceObject]:
        """Resolve a GameManager AudioSource field through its m_audioClip ref."""
        direct = self.find_named("AudioClip", field_name)
        if direct:
            return direct
        for manager in self.objects:
            if manager.type_name != "GameManager":
                continue
            reference = manager.data.get(field_name)
            source = self.resolve(reference, manager, {"AudioSource", "AudioClip"})
            if not source:
                continue
            if source.type_name == "AudioClip":
                return source
            clip_ref = source.data.get("m_audioClip")
            clip = self.resolve(clip_ref, source, {"AudioClip"})
            if clip:
                return clip
        return None


def _row_key(category: str, source: str, suffix: str) -> str:
    """Build a Paratranz key; only asset indexes retain the full namespace."""
    if category == "asset":
        key = f"asset|||{source}|||{suffix}"
    else:
        key = suffix
    if len(key) > MAX_TRANSLATION_KEY_LENGTH:
        raise ValueError(f"generated key exceeds {MAX_TRANSLATION_KEY_LENGTH} characters: {key[:120]}...")
    return key


def _is_underscore_placeholder(value: str) -> bool:
    stripped = value.strip()
    return bool(stripped) and set(stripped) == {"_"}


def _unique_rows(rows: Iterable[CsvRow]) -> list[CsvRow]:
    result: list[CsvRow] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        if not row.original.strip():
            continue
        key = (row.key, row.original)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def _data_rows(data: GameData) -> dict[str, list[CsvRow]]:
    rows: dict[str, list[CsvRow]] = {name: [] for name in ("dialogue", "choice", "item", "character_name", "client_info", "ending", "ui", "flow_context")}
    for item in data.dialogues:
        node = "none" if item.node_id is None else str(item.node_id)
        rows["dialogue"].append(CsvRow(_row_key("dialogue", item.source, f"{node}|||{item.speaker}|||{item.source_line}"), item.text))
    for item in data.choices:
        rows["choice"].append(CsvRow(_row_key("choice", item.source, f"{item.from_id}|||{item.option_id}|||{item.source_line}"), item.text))
    for item in data.items:
        rows["item"].append(CsvRow(_row_key("item", item.source, item.key_suffix), item.text))
    for name in sorted(data.character_names):
        rows["character_name"].append(CsvRow(_row_key("character_name", "GameManager.cs", name), name))
    for item in data.client_info:
        rows["client_info"].append(CsvRow(_row_key("client_info", item.source, item.key_suffix), item.text))
    for item in data.ending:
        rows["ending"].append(CsvRow(_row_key("ending", item.source, item.key_suffix), item.text))
    for item in data.ui:
        if not _is_underscore_placeholder(item.text):
            rows["ui"].append(CsvRow(_row_key("ui", item.source, item.key_suffix), item.text))
    for event in data.flow_events:
        node = "none" if event.node_id is None else str(event.node_id)
        details = f"event={event.event_type}; node={node}; line={event.source_line}; {event.details}"
        if event.parent_call:
            details += f"; trigger={event.parent_call}"
        rows["flow_context"].append(CsvRow(_row_key("flow", "GameManager.cs", f"{node}|||{event.event_type}|||{event.source_line}"), details))
    return {key: _unique_rows(value) for key, value in rows.items()}


def extract_ui_rows(index: ResourceIndex) -> list[CsvRow]:
    rows: list[CsvRow] = []
    for obj in index.objects:
        if obj.type_name not in {"TextMeshProUGUI", "Text", "TextMeshPro"}:
            continue
        for field_name in ("m_text", "m_Text"):
            value = obj.data.get(field_name)
            if isinstance(value, str) and value.strip():
                if _is_underscore_placeholder(value):
                    break
                rows.append(CsvRow(
                    _row_key("ui", obj.source, f"{obj.source}|||{obj.path_id}|||{obj.type_name}|||{obj.name}"),
                    value,
                ))
                break
    return _unique_rows(rows)


def _asset_rows(index: ResourceIndex) -> list[CsvRow]:
    relevant = {"GameObject", "AudioSource", "AudioClip", "Sprite", "Texture2D", "Animator", "AnimatorController", "AnimationClip", "Transform", "RectTransform"}
    rows: list[CsvRow] = []
    for obj in index.objects:
        if obj.type_name not in relevant:
            continue
        relative = obj.path.relative_to(index.root.parent).as_posix() if index.root.parent in obj.path.parents else obj.path.as_posix()
        content = f"type={obj.type_name}; name={obj.name}; source={obj.source}; path_id={obj.path_id}; path={relative}"
        rows.append(CsvRow(_row_key("asset", obj.type_name, f"{obj.source}|||{obj.path_id}|||{obj.name}|||{obj.path.name}"), content))
    return _unique_rows(rows)


def _enrich_flow_events(
    data: GameData,
    index: ResourceIndex,
    audio_aliases: Optional[dict[str, str]] = None,
) -> None:
    audio_aliases = audio_aliases or {}
    for event in data.flow_events:
        if event.event_type == "image" and event.details.startswith("image="):
            name = event.details.split("=", 1)[1]
            if name == "backgroundImage":
                event.details += "; reference=method-default"
                continue
            sprite = index.find_named("Sprite", name)
            if sprite:
                event.details += f"; file={sprite.path.relative_to(index.root.parent).as_posix()}"
                png = sprite.path.with_suffix(".png")
                if png.exists():
                    event.details += f"; image={png.relative_to(index.root.parent).as_posix()}"
            else:
                event.details += "; file=UNRESOLVED"
                index.unresolved.append(f"flow image; node={event.node_id}; line={event.source_line}; name={name}")
        if event.event_type in {"music", "ambience", "sound"}:
            match = re.search(r"(?:name|source)=([^;]+)", event.details)
            if not match:
                continue
            name = match.group(1).strip()
            if name == "nothing":
                event.details += "; audio=NO_AUDIO"
                continue
            field_name = audio_aliases.get(name, name)
            clip = index.resolve_audio_field(field_name)
            if clip:
                relative = clip.path.relative_to(index.root.parent).as_posix()
                alias_detail = f"; alias={field_name}" if field_name != name else ""
                event.details += f"; audio={clip.name}{alias_detail}; file={relative}"
            else:
                event.details += "; file=UNRESOLVED_AUDIO"
                index.unresolved.append(f"flow audio; node={event.node_id}; line={event.source_line}; name={name}")


def _write_rows(path: Path, rows: Iterable[CsvRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow([row.key, row.original, row.translated])


def run_extraction(project_root: Path, output_dir: Path) -> ExtractionStats:
    resources = project_root / "resources"
    decompiled = resources / "Assembly-CSharp-decompiled"
    data = GameData()
    game_manager = decompiled / "GameManager.cs"
    if game_manager.exists():
        data = parse_game_manager(game_manager)
    index = ResourceIndex.from_root(resources)
    ui_json_rows = extract_ui_rows(index)
    _enrich_flow_events(data, index, _parse_audio_aliases(game_manager))
    rows = _data_rows(data)
    rows["ui"] = _unique_rows([*rows["ui"], *ui_json_rows])
    rows["asset_index"] = _asset_rows(index)
    rows["unresolved_refs"] = [
        CsvRow(_row_key("unresolved_refs", "", str(number)), value)
        for number, value in enumerate(index.unresolved, 1)
    ]
    filenames = {
        "dialogue": "dialogue.csv",
        "choice": "choice.csv",
        "item": "item.csv",
        "character_name": "character_name.csv",
        "client_info": "client_info.csv",
        "ending": "ending.csv",
        "ui": "ui.csv",
        "flow_context": "flow_context.csv",
        "asset_index": "asset_index.csv",
        "unresolved_refs": "unresolved_refs.csv",
    }
    for category, filename in filenames.items():
        _write_rows(output_dir / filename, rows.get(category, []))
    return ExtractionStats(
        dialogue_count=len(rows["dialogue"]), choice_count=len(rows["choice"]), item_count=len(rows["item"]),
        character_name_count=len(rows["character_name"]), client_info_count=len(rows["client_info"]),
        ending_count=len(rows["ending"]), ui_count=len(rows["ui"]), flow_count=len(rows["flow_context"]),
        asset_count=len(rows["asset_index"]), unresolved_count=len(rows["unresolved_refs"]),
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    project_root = args.project_root.resolve()
    decompiled = project_root / "resources" / "Assembly-CSharp-decompiled"
    if not project_root.exists() or not decompiled.exists():
        parser.error(f"required directory does not exist: {decompiled}")
    output_dir = (args.output_dir or project_root / "resources" / "extracted").resolve()
    stats = run_extraction(project_root, output_dir)
    print(f"dialogue={stats.dialogue_count} choice={stats.choice_count} item={stats.item_count} character_name={stats.character_name_count}")
    print(f"client_info={stats.client_info_count} ending={stats.ending_count} ui={stats.ui_count}")
    print(f"flow={stats.flow_count} assets={stats.asset_count} unresolved={stats.unresolved_count}")
    print(f"output={output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
