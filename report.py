import json

def save_report(data, out):
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
