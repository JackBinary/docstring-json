# jsdoc Format and Behavior Specification

## 1. Purpose

`jsdoc` is a Python library for reading and writing JSON-like documents that support authoring-friendly extensions over strict JSON.

At parse time, `jsdoc` preprocesses source text and then delegates final decoding to Python's built-in `json` parser.

## 2. Data Model

The resulting runtime data model is standard JSON:

- Objects → Python `dict`
- Arrays → Python `list`
- Strings → Python `str`
- Numbers → Python `int`/`float`
- `true`/`false`/`null` → `True`/`False`/`None`

No custom runtime node types are introduced.

## 3. Supported Syntax Extensions

In addition to standard JSON syntax, `jsdoc` accepts the following extensions.

### 3.1 JavaScript-style comments

- Line comments: `// ...` (until newline)
- Block comments: `/* ... */`

Comments are removed before JSON parsing.

Comment markers occurring inside normal quoted JSON strings or inside triple-quoted blocks are treated as literal text.

### 3.2 Bare object keys

Unquoted keys are accepted when they match:

`[A-Za-z_$][A-Za-z0-9_$]*`

Examples of accepted bare keys:

- `name`
- `_private`
- `$cost`
- `camelCase`
- `__dunder__`

Examples not accepted as bare keys:

- `invalid key` (contains a space)
- keys beginning with a digit

### 3.3 Triple-quoted string blocks

String values may be written as:

`""" ... """`

These blocks are converted to JSON strings during preprocessing.

Delimiter validation rules:

- Quote runs used as delimiters must be in multiples of 3.
- Uneven runs (e.g. 5 or 7 quotes) are invalid.
- Unclosed triple-quoted blocks are invalid.

When valid, the inner text is transformed as follows:

- Outer whitespace is stripped.
- If `collapse_whitespace=False` (default): line breaks are preserved (after outer strip).
- If `collapse_whitespace=True`: internal whitespace is normalized with `" ".join(inner.split())`.

## 4. Parse Pipeline (Normative Implementation Behavior)

Given input text, preprocessing is applied in this order:

1. Extract and replace triple-quoted blocks with JSON-string placeholders; store the raw content as Python strings.
2. Strip comments from remaining text.
3. Quote bare keys.
4. Decode with `json.loads` (placeholders parse as regular strings).
5. Walk the parsed data structure and replace placeholder strings with the stored Python strings.

This ordering guarantees that comment stripping and bare-key quoting do not alter text inside triple-quoted blocks, and avoids manual JSON escaping of triple-quoted content.

## 5. Public API

### 5.1 `loads(text, *, collapse_whitespace=False, **kwargs)`

Parses jsdoc text to Python data.

- If the text contains any of `"""`, `//`, or `/*`, preprocessing is always run first.
- Otherwise, `json.loads` is attempted directly.
- If direct JSON parse fails, preprocessing is attempted as fallback.
- Additional keyword arguments are passed to `json.loads`.

### 5.2 `load(path, *, collapse_whitespace=False, encoding="utf-8", **kwargs)`

Reads a file and delegates to `loads`.

### 5.3 `dumps(data, *, indent=2, threshold=80)`

Serializes Python data to jsdoc-like text.

Behavior:

1. Calls `json.dumps(data, indent=indent, ensure_ascii=False)`.
2. Scans string tokens and upgrades some to triple-quoted blocks.

Upgrade heuristic (`_needs_triple_quote`):

- `len(value) > threshold`, or
- value contains `<`

If upgraded, output token format is:

`"""\n      <value>\n    """`

### 5.4 `dump(data, path, *, indent=2, threshold=80, encoding="utf-8")`

Writes `dumps(...)` output to a file.

## 6. Error Semantics

Custom exceptions:

- `JSDocError`: base class
- `JSDocParseError`: preprocessing/format validation error

`JSDocParseError` is raised for invalid triple-quote delimiter structure (uneven or unclosed triple-quoted blocks).

JSON syntax errors that remain after preprocessing (for example trailing commas) propagate as `json.JSONDecodeError`.

## 7. Backend Selection

At import time, `jsdoc` attempts to use a Cython backend (`jsdoc._cython_backend`) for preprocessing.

- On success: `USING_CYTHON_BACKEND = True`
- On failure: Python backend (`jsdoc._python_backend`) is used and `USING_CYTHON_BACKEND = False`

Both backends implement equivalent preprocessing behavior.

## 8. Compatibility Notes

- Strict JSON files are valid input.
- `.jsdoc` is a convention; parser behavior is content-based.
- Trailing commas are not supported (same as standard JSON).
- Unclosed block comments are not explicitly validated during preprocessing; such input may fail later during JSON decode.

## 9. Non-goals (Current Implementation)

Current behavior does **not** include:

- JSON5 features beyond listed extensions (e.g. single-quoted strings, hexadecimal numbers)
- Automatic support for trailing commas
- Preservation of original comments/formatting during parse/dump round-trip
