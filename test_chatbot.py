"""
Automated Test Suite for FAQ Chatbot
Validates NLP preprocessing, cosine similarity matcher, and fallback behavior.
"""

import unittest
from nlp_preprocessor import TextPreprocessor
from faq_matcher import FAQMatcher
from chatbot import FAQChatbot


class TestFAQChatbot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.preprocessor = TextPreprocessor()
        cls.chatbot = FAQChatbot()

    def test_preprocessor_lowercasing_and_punctuation(self):
        sample = "What's the Order Tracking NUMBER?!"
        cleaned = self.preprocessor.preprocess(sample)
        self.assertNotIn("?", cleaned)
        self.assertNotIn("!", cleaned)
        self.assertIn("track", cleaned)
        self.assertIn("order", cleaned)

    def test_greeting_queries(self):
        result = self.chatbot.get_response("hello")
        self.assertTrue(result["matched"])
        self.assertGreaterEqual(result["confidence"], 0.5)
        self.assertIn("AI FAQ Assistant", result["bot_response"])

    def test_order_tracking_query(self):
        result = self.chatbot.get_response("Where can I track my shipment?")
        self.assertTrue(result["matched"])
        self.assertIn("My Orders", result["bot_response"])

    def test_return_policy_query(self):
        result = self.chatbot.get_response("How many days do I have to return an item?")
        self.assertTrue(result["matched"])
        self.assertIn("30-day", result["bot_response"])

    def test_payment_methods_query(self):
        result = self.chatbot.get_response("What payment methods do you accept?")
        self.assertTrue(result["matched"])
        self.assertIn("PayPal", result["bot_response"])

    def test_out_of_domain_query(self):
        result = self.chatbot.get_response("What is the capital of Mars?")
        self.assertFalse(result["matched"])
        self.assertLess(result["confidence"], 0.25)
        self.assertIn("not entirely sure", result["bot_response"])
        self.assertGreater(len(result["suggestions"]), 0)


if __name__ == "__main__":
    unittest.main()
