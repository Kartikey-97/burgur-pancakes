import json

def parse_json_stream(chunks):
    accumulated = ""
    in_question = False
    extracted_question = ""
    for chunk in chunks:
        accumulated += chunk
        # very simple heuristic: look for "next_question": "
        if not in_question:
            marker = '"next_question": "'
            idx = accumulated.find(marker)
            if idx != -1:
                in_question = True
                # yield whatever is after the marker
                rest = accumulated[idx + len(marker):]
                # but wait, the chunk might contain the end quote too!
                end_idx = rest.find('"')
                if end_idx != -1:
                    yield rest[:end_idx]
                    in_question = False
                else:
                    if rest:
                        yield rest
        else:
            # we are inside the question string
            end_idx = chunk.find('"')
            if end_idx != -1:
                yield chunk[:end_idx]
                in_question = False
            else:
                yield chunk

chunks = [
    '{\n  "score": 3.5,\n  "next_question": "How ',
    'would you design ',
    'a distributed system?\\nI need details."\n}'
]

for text in parse_json_stream(chunks):
    print("YIELD:", repr(text))
