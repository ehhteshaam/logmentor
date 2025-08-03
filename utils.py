import re

def structure_logs(raw_text):
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ \[(.*?)\] (.*)")
    structured = []
    for line in raw_text.splitlines():
        match = pattern.match(line)
        if match:
            structured.append({
                "timestamp": match.group(1),
                "level": match.group(2),
                "message": match.group(3)
            })
    return structured

def chunk_structured_logs(logs, chunk_size=10):
    chunks = []
    for i in range(0, len(logs), chunk_size):
        chunk = logs[i:i+chunk_size]
        chunk_text = "\n".join([f"{log['timestamp']} [{log['level']}] {log['message']}" for log in chunk])
        chunks.append(chunk_text)
    return chunks
