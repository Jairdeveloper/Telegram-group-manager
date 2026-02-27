#!/usr/bin/env python3
import sys
import json

"""Small helper to extract chat_id from a Telegram update payload.

Usage:
  # read from a file
  python scripts/get_chat_id.py sample_update.json

  # or read from stdin
  cat sample_update.json | python scripts/get_chat_id.py
"""

def load_input():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)


def main():
    try:
        data = load_input()
    except Exception as e:
        print("Failed to read JSON input:", e, file=sys.stderr)
        sys.exit(2)

    chat = data.get("message") or data.get("edited_message")
    if not chat:
        print("No message or edited_message found in payload", file=sys.stderr)
        sys.exit(1)

    try:
        chat_id = chat["chat"]["id"]
    except Exception as e:
        print("Failed to extract chat id:", e, file=sys.stderr)
        sys.exit(3)

    print("CHAT_ID:", chat_id)


if __name__ == '__main__':
    main()
