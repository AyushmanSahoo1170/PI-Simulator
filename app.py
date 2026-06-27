from flask import Flask, jsonify, render_template, request

from engine import METHODS, count_correct_decimals, reference_pi, timed

app = Flask(__name__)

TARGETS = {8, 16, 32}
DEFAULT_SAMPLES = 200_000
MAX_SAMPLES = 2_000_000
STATISTICAL_SHOWN = 10

PUBLIC_FIELDS = (
    "label", "year", "category", "tier", "mode", "work_label", "formula", "blurb"
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/methods")
def methods():
    return jsonify([
        {"id": mid, "runnable": meta["mode"] != "none",
         **{field: meta[field] for field in PUBLIC_FIELDS}}
        for mid, meta in METHODS.items()
    ])


@app.post("/api/estimate")
def estimate():
    payload = request.get_json(force=True) or {}
    meta = METHODS.get(payload.get("method"))
    if meta is None:
        return jsonify({"error": "Unknown method."}), 400
    if meta["mode"] == "none":
        return jsonify({"error": f"{meta['label']} is a reference entry — {meta['blurb']}"}), 400
    target = int(payload.get("decimals", 32))
    if target not in TARGETS:
        return jsonify({"error": "Decimals must be 8, 16 or 32."}), 400

    if meta["mode"] == "samples":
        samples = max(1_000, min(int(payload.get("samples", DEFAULT_SAMPLES)), MAX_SAMPLES))
        (value, work), seconds = timed(meta["run"], samples)
        shown = STATISTICAL_SHOWN
    else:
        (value, work), seconds = timed(meta["run"], target)
        shown = target

    full_text = str(value)
    correct = count_correct_decimals(full_text)
    passed = meta["mode"] == "target" and correct >= target
    return jsonify({
        "id": payload.get("method"),
        "label": meta["label"],
        "mode": meta["mode"],
        "target": target,
        "shown": shown,
        "value": full_text[: shown + 2],
        "reference": reference_pi(shown),
        "correct": correct,
        "bonus": max(0, correct - target) if meta["mode"] == "target" else 0,
        "work": work,
        "work_label": meta["work_label"],
        "ms": round(seconds * 1000, 3),
        "passed": passed,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
