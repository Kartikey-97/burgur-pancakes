def parse_text_stream(chunks):
    accumulated = ""
    in_question = False
    for chunk in chunks:
        if in_question:
            yield chunk
        else:
            accumulated += chunk
            marker = "NEXT_QUESTION:"
            idx = accumulated.find(marker)
            if idx != -1:
                in_question = True
                rest = accumulated[idx + len(marker):].lstrip()
                if rest:
                    yield rest

chunks = [
    "SCORE: 3.5\n",
    "NEEDS_FOLLOWUP: false\n",
    "NEXT_QUESTION:\nHow ",
    "would you design ",
    "a distributed system?"
]

for text in parse_text_stream(chunks):
    print("YIELD:", repr(text))
