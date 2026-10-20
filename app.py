"""
Flask Web Server for FAQ Chatbot
Exposes REST APIs and serves modern interactive Chat UI.
"""

import os
from flask import Flask, render_template, request, jsonify
from chatbot import FAQChatbot

app = Flask(__name__)

# Initialize FAQ Chatbot instance
current_dir = os.path.dirname(os.path.abspath(__file__))
faq_data_file = os.path.join(current_dir, "faq_data.json")
chatbot = FAQChatbot(data_path=faq_data_file)


@app.route("/")
def home():
    """Serves the main Chatbot interface."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST endpoint: processes incoming user question and returns matching FAQ answer.
    Payload: {"message": "How do I track my order?"}
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "status": "error",
            "reply": "Please provide a valid question.",
            "confidence": 0.0,
            "matched": False,
            "suggestions": []
        }), 400

    response_data = chatbot.get_response(message)

    return jsonify({
        "status": "success",
        "reply": response_data["bot_response"],
        "matched": response_data["matched"],
        "confidence": response_data["confidence"],
        "confidence_percent": int(response_data["confidence"] * 100),
        "best_faq": response_data.get("best_faq"),
        "suggestions": response_data.get("suggestions", []),
        "latency_ms": response_data.get("latency_ms", 0),
        "timestamp": response_data["timestamp"]
    })


@app.route("/api/faqs", methods=["GET"])
def get_faqs():
    """Returns the full catalog of FAQs grouped by category."""
    all_faqs = chatbot.get_all_faqs()
    categories = {}
    for faq in all_faqs:
        cat = faq.get("category", "General")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": faq.get("id"),
            "question": faq.get("question"),
            "answer": faq.get("answer")
        })
    return jsonify({
        "status": "success",
        "total": len(all_faqs),
        "categories": categories,
        "faqs": all_faqs
    })


@app.route("/api/reset", methods=["POST"])
def reset_session():
    """Resets conversational memory."""
    chatbot.clear_history()
    return jsonify({
        "status": "success",
        "message": "Chat history cleared successfully."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting FAQ Chatbot Server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
