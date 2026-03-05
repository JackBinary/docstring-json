import docstring_json
import json
import os
import sys
import traceback

# Change to the project root directory
os.chdir(os.path.dirname(os.path.dirname(__file__)))

# --- Test file contents ---

FILES = {
    "test01_basic.djson": """{
  // a comment
  name: "Alice",
  bio: \"\"\"\n    Hello world.\n    This is a test.\n  \"\"\"
}""",

    "test02_comments_in_strings.djson": """{
  "url": "https://example.com/path",
  "regex": "match /* this */ and // that",
  "code": \"\"\"\n    <code>let x = 1; // not a comment</code>\n    <code>let y = /* also not */ 2;</code>\n  \"\"\"
}""",

    "test03_nested_bare_keys.djson": """{
  characters: {
    hero: {
      name: "Kael",
      stats: {
        str: 10,
        dex: 14,
        wis: 8
      }
    },
    villain: {
      name: "Morrax",
      stats: {
        str: 16,
        dex: 9,
        wis: 12
      }
    }
  }
}""",

    "test04_empty_and_short_tq.djson": """{
  "empty": \"\"\"\"\"\",
  "just_spaces": \"\"\"     \"\"\",
  "one_word": \"\"\"hello\"\"\",
  "one_line": \"\"\"this has no newlines at all\"\"\"
}""",

    "test05_special_chars.djson": """{
  "escaped": \"\"\"\n    She said "hello" and then left.\n    Path: C:\\Users\\test\\file.txt\n    Tab\tseparated\tvalues\n  \"\"\"
}""",

    "test06_comment_heavy.djson": """{
  // top-level comment

  /* 
   * Block comment with
   * multiple lines
   */

  name: "test", // inline after value

  // orphan comment between keys

  value: 42 // trailing
}""",

    "test07_arrays.djson": """{
  tags: ["fire", "ice", "lightning"],
  techniques: [
    {
      name: "Fireball",
      desc: \"\"\"\n        <p>Hurl a ball of <strong>fire</strong>\n        at your enemies.</p>\n      \"\"\"
    },
    {
      name: "Frost Nova",
      desc: \"\"\"\n        <p>Freeze all enemies within\n        a 10m radius.</p>\n      \"\"\"
    }
  ]
}""",

    "test08_preserve_newlines.djson": """{
  poem: \"\"\"\n    roses are red\n    violets are blue\n    this parser is cool\n    and so are you\n  \"\"\"
}""",

    "test09_dollar_underscore_keys.djson": """{
  _private: "yes",
  $cost: 9.99,
  __dunder__: "python vibes",
  normal_key_99: true
}""",

    "test10_real_world.djson": """{
  // ==================
  // TECHNIQUE DATABASE
  // ==================

  "Battle in the Mind": {
    rank: "2",
    type: "Combat",
    approach: "Fortune",
    skill: "",
    flavor: \"\"\"\n      An elite who has survived enough engagements learns to recognize\n      the signals an opponent does not intend to reveal.\n    \"\"\",
    description: \"\"\"\n      <h3>Activation:</h3>\n      <p>When you make an Initiative check for a duel using your\n      Fortune Approach, you may spend (op) in the following way:</p>\n      <ul>\n        <li><strong>Fortune (op):</strong> Name two approaches.</li>\n        <li><strong>Fortune (op)+:</strong> Choose a technique category.</li>\n      </ul>\n    \"\"\"
  },

  /*
   * Quick Draw is a simple rank 1 technique
   * that every gunslinger should know.
   */
  "Quick Draw": {
    rank: "1",
    type: "Combat",
    approach: "Vigor",
    skill: "",
    flavor: "No hesitation. No second thoughts. Just draw.",
    description: \"\"\"\n      <h3>Activation:</h3>\n      <p>As a free action at the start of your turn, draw a weapon.</p>\n    \"\"\"
  },

  // Utility techniques go here
  "Field Medic": {
    rank: "1",
    type: "Utility",
    approach: "Reason",
    skill: "Medicine",
    flavor: \"\"\"\n      A steady hand and a cool head are worth more\n      than any miracle drug in the field.\n    \"\"\",
    description: \"\"\"\n      <h3>Activation:</h3>\n      <p>Spend an action to stabilize an adjacent wounded ally.\n      Roll <strong>Reason + Medicine</strong>.</p>\n    \"\"\"
  }
}"""
}

# --- Helpers ---

passed = 0
failed = 0


def run_test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAIL  {name}")
        traceback.print_exc()
        print()
        failed += 1


def check_files_exist():
    """Ensure all test files exist on disk."""
    expected_files = [
        "test01_basic.djson",
        "test02_comments_in_strings.djson",
        "test03_nested_bare_keys.djson",
        "test04_empty_and_short_tq.djson",
        "test05_special_chars.djson",
        "test06_comment_heavy.djson",
        "test07_arrays.djson",
        "test08_preserve_newlines.djson",
        "test09_dollar_underscore_keys.djson",
        "test10_real_world.djson",
        "test12_comments_edge_cases.djson",
        "test13_bare_keys_edge.djson",
        "test14_triple_quotes_edge.djson",
        "test15_invalid_trailing_comma.djson",
        "test16_deep_nesting.djson",
        "test17_empty_structures.djson",
    ]
    missing = []
    for filename in expected_files:
        path = os.path.join("tests", "test_files", filename)
        if not os.path.exists(path):
            missing.append(path)
    if missing:
        print(f"Missing test files: {missing}")
        print("Run 'python create_test_files.py' to create them.")
        sys.exit(1)


def cleanup_roundtrip():
    """Clean up the roundtrip test file."""
    path = os.path.join("tests", "test_files", "test10_roundtrip.djson")
    if os.path.exists(path):
        os.remove(path)


# --- Tests ---

def test01_basic():
    data = docstring_json.load("tests/test_files/test01_basic.djson")
    assert data["name"] == "Alice"
    assert "Hello world." in data["bio"]
    assert "This is a test." in data["bio"]
    assert "\n" in data["bio"], "newlines should be preserved by default"


def test02_comments_in_strings():
    data = docstring_json.load("tests/test_files/test02_comments_in_strings.djson")
    assert data["url"] == "https://example.com/path"
    assert "/* this */" in data["regex"]
    assert "// that" in data["regex"]
    assert "// not a comment" in data["code"]
    assert "/* also not */" in data["code"]


def test03_nested_bare_keys():
    data = docstring_json.load("tests/test_files/test03_nested_bare_keys.djson")
    assert data["characters"]["hero"]["name"] == "Kael"
    assert data["characters"]["villain"]["stats"]["str"] == 16
    assert data["characters"]["hero"]["stats"]["wis"] == 8


def test04_empty_and_short_tq():
    data = docstring_json.load("tests/test_files/test04_empty_and_short_tq.djson")
    assert data["empty"] == ""
    assert data["just_spaces"] == ""
    assert data["one_word"] == "hello"
    assert data["one_line"] == "this has no newlines at all"


def test05_special_chars():
    data = docstring_json.load("tests/test_files/test05_special_chars.djson")
    assert 'said "hello"' in data["escaped"]
    assert "C:\\Users\\test\\file.txt" in data["escaped"]


def test06_comment_heavy():
    data = docstring_json.load("tests/test_files/test06_comment_heavy.djson")
    assert data["name"] == "test"
    assert data["value"] == 42


def test07_arrays():
    data = docstring_json.load("tests/test_files/test07_arrays.djson")
    assert data["tags"] == ["fire", "ice", "lightning"]
    assert len(data["techniques"]) == 2
    assert "<strong>fire</strong>" in data["techniques"][0]["desc"]
    assert data["techniques"][1]["name"] == "Frost Nova"


def test08_collapse_whitespace():
    data = docstring_json.load("tests/test_files/test08_preserve_newlines.djson")
    assert "\n" in data["poem"], "newlines should be preserved by default"
    assert "roses are red" in data["poem"]
    assert "and so are you" in data["poem"]


def test09_dollar_underscore_keys():
    data = docstring_json.load("tests/test_files/test09_dollar_underscore_keys.djson")
    assert data["_private"] == "yes"
    assert data["$cost"] == 9.99
    assert data["__dunder__"] == "python vibes"
    assert data["normal_key_99"] is True


def test10_real_world():
    data = docstring_json.load("tests/test_files/test10_real_world.djson")
    assert "Battle in the Mind" in data
    assert "Quick Draw" in data
    assert "Field Medic" in data
    assert data["Quick Draw"]["rank"] == "1"
    assert "<h3>Activation:</h3>" in data["Field Medic"]["description"]


def test11_roundtrip():
    original = docstring_json.load("tests/test_files/test10_real_world.djson")
    docstring_json.dump(original, "tests/test_files/test10_roundtrip.djson")
    reloaded = docstring_json.load("tests/test_files/test10_roundtrip.djson")
    assert original == reloaded, "round-trip data mismatch"


def test12_comments_edge_cases():
    data = docstring_json.load("tests/test_files/test12_comments_edge_cases.djson")
    assert data["name"] == "test"
    assert data["value"] == 42
    assert data["array"] == ["item1", "item2"]
    assert data["obj"]["key"] == "value"


def test13_bare_keys_edge():
    data = docstring_json.load("tests/test_files/test13_bare_keys_edge.djson")
    assert data["_underscore"] == "yes"
    assert data["$dollar"] == "yes"
    assert data["key123"] == "numbers"
    assert data["camelCase"] == "mixed"
    assert data["PascalCase"] == "upper"
    assert data["__dunder__"] == "double"
    assert data["_private_key"] == "private"
    assert data["$special"] == 99.99


def test14_triple_quotes_edge():
    data = docstring_json.load("tests/test_files/test14_triple_quotes_edge.djson")
    assert "multiple lines" in data["multiline"]
    assert "// not a comment" in data["multiline"]
    assert "/* not a comment */" in data["multiline"]
    assert 'She said "hello"' in data["with_quotes"]
    assert data["empty"] == ""
    assert data["single_line"] == "no newlines"


def test15_invalid_trailing_comma():
    try:
        docstring_json.load("tests/test_files/test15_invalid_trailing_comma.djson")
        assert False, "Should have failed due to trailing comma"
    except json.JSONDecodeError:
        pass  # Expected


def test16_deep_nesting():
    data = docstring_json.load("tests/test_files/test16_deep_nesting.djson")
    assert data["level1"]["level2"]["level3"]["level4"]["deep"] == "value"
    assert data["array"][0]["nested"][0]["deep"] == "array value"


def test17_empty_structures():
    data = docstring_json.load("tests/test_files/test17_empty_structures.djson")
    assert data["empty_obj"] == {}
    assert data["empty_arr"] == []
    assert data["nested_empty"]["empty"] == {}
    assert data["nested_empty"]["arr"] == []


def test18_invalid_uneven_triple_quotes():
  invalid_seven = '{ broken: """"""" }'
  invalid_five = '{ broken: """"" }'

  for bad_input in (invalid_seven, invalid_five):
    try:
      docstring_json.loads(bad_input)
      assert False, "Should have failed due to uneven triple quotes"
    except docstring_json.DjsonParseError:
      pass


# --- Main ---

if __name__ == "__main__":
    print("Checking test files...")
    check_files_exist()
    print("All test files present.")
    print()

    tests = [
        ("01 basic parse + collapse",       test01_basic),
        ("02 comments inside strings",       test02_comments_in_strings),
        ("03 nested bare keys",              test03_nested_bare_keys),
        ("04 empty/short triple-quotes",     test04_empty_and_short_tq),
        ("05 special chars (quotes/backslash/tab)", test05_special_chars),
        ("06 comment-heavy file",            test06_comment_heavy),
        ("07 arrays with triple-quotes",     test07_arrays),
        ("08 collapse_whitespace mode",      test08_collapse_whitespace),
        ("09 $_underscore bare keys",        test09_dollar_underscore_keys),
        ("10 real-world multi-entry",        test10_real_world),
        ("11 dump/load round-trip",          test11_roundtrip),
        ("12 comments edge cases",           test12_comments_edge_cases),
        ("13 bare keys edge cases",          test13_bare_keys_edge),
        ("14 triple quotes edge cases",      test14_triple_quotes_edge),
        ("15 invalid trailing comma",        test15_invalid_trailing_comma),
        ("16 deep nesting",                  test16_deep_nesting),
        ("17 empty structures",              test17_empty_structures),
        ("18 invalid uneven triple quotes",  test18_invalid_uneven_triple_quotes),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print()
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")

    cleanup_roundtrip()
    sys.exit(1 if failed else 0)