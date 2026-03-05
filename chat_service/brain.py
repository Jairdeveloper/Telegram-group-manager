"""Default brain data (patterns and fallback responses).

Kept in `chat_service` so the API runtime doesn't depend on legacy entrypoints.
"""

from __future__ import annotations


def get_default_brain() -> tuple:
    """Return pattern/response tables for the default rule-based agent."""

    default_responses = [
        ["That's", "interesting,", "tell", "me", "more"],
        ["I", "see.", "Could", "you", "elaborate?"],
        ["That's", "a", "great", "point"],
        ["I", "understand.", "What", "else?"],
        ["In", "other", "words,", "you're", "saying...?"],
        ["Can", "you", "give", "me", "an", "example?"],
        ["That", "makes", "sense"],
        ["I", "appreciate", "your", "thoughts"],
    ]

    pattern_responses = [
        # SALUDOS
        [["hello", 0], ["Hello!", "It's", "nice", "to", "meet", "you"]],
        [["hi", 0], ["Hi", "there!", "How", "can", "I", "help?"]],
        [["hey", 0], ["Hey!", "What's", "on", "your", "mind?"]],
        [["good", "morning"], ["Good", "morning!", "Ready", "to", "chat?"]],
        [["good", "afternoon"], ["Good", "afternoon!", "How", "are", "you?"]],
        [["good", "evening"], ["Good", "evening!", "Nice", "to", "see", "you"]],
        # DESPEDIDAS
        [["goodbye", 0], ["Goodbye!", "It", "was", "great", "talking", "to", "you"]],
        [["bye", 0], ["See", "you", "later!", "Take", "care"]],
        # PRESENTACION
        [
            [0, "my", "name", "is", [1, "name"], 0],
            ["Pleased", "to", "meet", "you,", [1, "name"], "!"],
        ],
        # COMO ESTAS
        [["how", "are", "you"], ["I'm", "doing", "great,", "thanks", "for", "asking!"]],
        [["how", "are", "you", "doing"], ["Doing", "well!", "What", "about", "you?"]],
        # ESTADO DEL USUARIO
        [
            ["i", "am", [1, "feeling"], 0],
            ["I'm", "sorry", "to", "hear", "you're", [1, "feeling"]],
        ],
        # PREFERENCIAS
        [
            ["i", "like", [1, "thing"], 0],
            [
                [1, "thing"],
                "is",
                "great!",
                "Why",
                "do",
                "you",
                "enjoy",
                [1, "thing"],
                "?",
            ],
        ],
        [
            ["i", "hate", [1, "thing"], 0],
            ["I", "see.", "It", "sounds", "like", [1, "thing"], "isn't", "for", "you"],
        ],
        # RELACIONES
        [[[1, "subject"], "loves", [0, "object"]], ["That's", "beautiful!"]],
        [[[1, "person"], "is", "my", "friend"], ["That's", "lovely!"]],
        # NECESIDADES
        [
            ["i", "need", [1, "object"], 0],
            ["Why", "do", "you", "need", [1, "object"], "?"],
        ],
        [["help", "me"], ["Of", "course!", "I'm", "here", "to", "help"]],
        # PREGUNTAS
        [
            ["what", "is", [1, "topic"], 0],
            ["That's", "an", "interesting", "question", "about", [1, "topic"]],
        ],
        # AGRADECIMIENTO
        [["thanks", 0], ["You're", "welcome!", "Happy", "to", "help"]],
        [["thank", "you"], ["My", "pleasure!"]],
        # CONFIRMACION
        [["yes", 0], ["Great!"]],
        [["no", 0], ["I", "understand"]],
        # INFORMACION DEL BOT
        [
            ["who", "are", "you"],
            ["I'm", "an", "AI", "chatbot", "created", "to", "chat"],
        ],
        [
            ["what", "can", "you", "do"],
            ["I", "can", "have", "conversations", "and", "help", "with", "ideas"],
        ],
    ]

    return pattern_responses, default_responses

