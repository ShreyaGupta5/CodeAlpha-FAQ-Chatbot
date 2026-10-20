"""
Core Chatbot Engine & Interactive CLI
Binds preprocessing and matching engines into a cohesive FAQ conversational agent.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

from faq_matcher import FAQMatcher


class FAQChatbot:
    """
    Intelligent FAQ Chatbot.
    Features:
    - Cosine similarity matching via TF-IDF vector space
    - Confidence scoring & fallback suggestions
    - Conversation memory log
    - Flexible data source loading
    """

    def __init__(self, data_path: str = None, confidence_threshold: float = 0.25):
        if data_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "faq_data.json")
            csv_path = os.path.join(base_dir, "faqs.csv")
            data_path = json_path if os.path.exists(json_path) else csv_path
            
        self.matcher = FAQMatcher(data_path=data_path, confidence_threshold=confidence_threshold)
        self.history: List[Dict[str, Any]] = []

    def get_response(self, user_message: str) -> Dict[str, Any]:
        """
        Processes a user query and returns a structured response dictionary.
        """
        start_time = time.time()
        match_result = self.matcher.find_match(user_message)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": match_result["answer"],
            "matched": match_result["matched"],
            "confidence": match_result["confidence"],
            "best_faq": match_result.get("best_faq"),
            "suggestions": match_result.get("suggestions", []),
            "latency_ms": latency_ms
        }
        self.history.append(record)
        return record

    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Returns the full list of FAQs."""
        return self.matcher.faqs

    def clear_history(self):
        """Resets the conversation history."""
        self.history = []


def run_cli():
    """Runs an interactive command-line interface for the FAQ chatbot."""
    chatbot = FAQChatbot()
    
    print("=" * 65)
    print("🤖 Welcome to the CodeAlpha FAQ Chatbot!")
    print("=" * 65)
    print("Ask any question regarding Orders, Shipping, Returns, Payments, etc.")
    print("Type 'help' for instructions, 'faqs' to list questions, or 'quit'/'exit' to leave.")
    print("-" * 65)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not user_input:
            continue

        lowered = user_input.lower()
        if lowered in ['quit', 'exit', 'bye', 'q']:
            print("\nBot: Thank you for chatting! Have a wonderful day! 👋\n")
            break
        elif lowered == 'help':
            print("\n[Commands Guide]:")
            print(" - 'faqs': View all available FAQ topics")
            print(" - 'history': View your chat history count")
            print(" - 'clear': Clear conversation history")
            print(" - 'quit': Exit the chatbot")
            continue
        elif lowered == 'faqs':
            print("\n--- Available FAQ Topics ---")
            for idx, item in enumerate(chatbot.get_all_faqs(), 1):
                print(f"{idx}. [{item.get('category', 'FAQ')}] {item.get('question')}")
            continue
        elif lowered == 'clear':
            chatbot.clear_history()
            print("\n[Chat history cleared]")
            continue
        elif lowered == 'history':
            print(f"\n[Total messages in session: {len(chatbot.history)}]")
            continue

        # Get response
        result = chatbot.get_response(user_input)
        confidence_pct = int(result['confidence'] * 100)
        
        status_badge = "✅ High Match" if result["matched"] else "⚠️ Low Confidence"
        print(f"\nBot [{status_badge} - {confidence_pct}%]:")
        print(f"{result['bot_response']}")
        
        if not result["matched"] and result["suggestions"]:
            print("\n💡 Suggested Related Questions:")
            for s in result["suggestions"][:3]:
                print(f"  • {s['question']}")


if __name__ == "__main__":
    run_cli()
