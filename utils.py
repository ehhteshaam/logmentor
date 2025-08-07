import re
import json

def structure_logs(raw_text):
    structured = []

    # Pattern for structured text logs
    text_log_pattern = re.compile(
        r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:,\d+)?\s+\[?(\w+)\]?\s+(.*)"
    )

    current_log = None

    for line in raw_text.splitlines():
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Try JSON log
        try:
            parsed = json.loads(line)
            if all(k in parsed for k in ("timestamp", "level", "message")):
                if current_log:
                    structured.append(current_log)
                current_log = {
                    "timestamp": parsed["timestamp"],
                    "level": parsed["level"],
                    "message": parsed["message"]
                }
                continue
        except json.JSONDecodeError:
            pass  # not a JSON line

        # Try text log
        match = text_log_pattern.match(line)
        if match:
            if current_log:
                structured.append(current_log)
            current_log = {
                "timestamp": match.group(1),
                "level": match.group(2),
                "message": match.group(3)
            }
        else:
            # Unstructured line: append to current log or create UNKNOWN
            if current_log:
                current_log["message"] += "\n" + line
            else:
                current_log = {
                    "timestamp": "",
                    "level": "UNKNOWN",
                    "message": line
                }

    if current_log:
        structured.append(current_log)

    return structured


def chunk_structured_logs(logs, chunk_size=10):
    chunks = []
    for i in range(0, len(logs), chunk_size):
        chunk = logs[i:i + chunk_size]
        chunk_text = "\n".join(
            [f"{log['timestamp']} [{log['level']}] {log['message']}" for log in chunk]
        )
        chunks.append(chunk_text)
    return chunks
