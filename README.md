# docstring-json
[![Tests](https://github.com/JackBinary/docstring-json/actions/workflows/tests.yml/badge.svg)](https://github.com/JackBinary/docstring-json/actions/workflows/tests.yml)
[![Security](https://github.com/JackBinary/docstring-json/actions/workflows/security.yml/badge.svg)](https://github.com/JackBinary/docstring-json/actions/workflows/security.yml)
[![Build](https://github.com/JackBinary/docstring-json/actions/workflows/build.yml/badge.svg)](https://github.com/JackBinary/docstring-json/actions/workflows/build.yml)

`docstring-json` is a Python parser for **JSON with comments and docstrings**.

It lets you keep human-friendly documentation directly inside JSON-like files while still loading data into normal Python dictionaries and lists.

## Why docstring-json?

Standard JSON is strict and does not allow comments or multiline doc-style strings. `docstring-json` extends JSON with practical authoring features:

- JavaScript-style comments (`//` and `/* ... */`)
- Bare keys (unquoted identifiers)
- Triple-quoted docstrings (`""" ... """`) for multiline text

After preprocessing, the content is parsed with Python’s built-in `json` parser.

## Installation

```bash
pip install docstring-json
```

## Quick Start

### Parse from a string

```python
import docstring_json

text = """
{
  // Display settings
  title: "Campaign Handbook",

  description: """
    A player-facing handbook.
    Includes lore, rules, and examples.
  """,

  page_count: 128
}
"""

data = docstring_json.loads(text)
print(data["title"])
print(data["description"])
```

### Parse from a file

```python
import docstring_json

data = docstring_json.load("config.djson")
print(data)
```

### Dump data back to .djson

```python
import docstring_json

data = {
    "name": "Field Manual",
    "notes": "This is a long block of descriptive text.",
}

docstring_json.dump(data, "output.djson")
```

## Comment and Docstring Behavior

- Comments are removed before JSON parsing.
- Triple-quoted values are converted into JSON strings.
- By default, line breaks inside triple-quoted blocks are preserved.
- Use `collapse_whitespace=True` to normalize all whitespace into single spaces.

```python
import docstring_json

value = docstring_json.loads(
    '{ text: """line 1\nline 2\nline 3""" }',
)

print(value["text"])
```

## Error Handling

`docstring-json` raises custom parse errors for malformed djson syntax such as uneven or unclosed triple-quote delimiters.

```python
import docstring_json

try:
    docstring_json.loads('{ bad: """"" }')
except docstring_json.DjsonParseError as exc:
    print(f"Invalid djson: {exc}")
```

For standard JSON syntax problems (for example trailing commas), Python’s `json.JSONDecodeError` is raised.

## API

- `docstring_json.loads(text, *, collapse_whitespace=False, **kwargs)`
- `docstring_json.load(path, *, collapse_whitespace=False, encoding="utf-8", **kwargs)`
- `docstring_json.dumps(data, *, indent=2, threshold=80)`
- `docstring_json.dump(data, path, *, indent=2, threshold=80, encoding="utf-8")`

## Use Cases

- Config files with inline explanations
- Content databases with rich multiline descriptions
- Human-authored JSON-like files that need documentation context

## License

MIT