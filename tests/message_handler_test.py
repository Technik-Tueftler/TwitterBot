#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File for testing the message handling functions in message_handler.py
"""
import unittest
from source.message_handler import analyze_message, decompose_tweet_url, extract_expand_url


class AnalyzeMessageTest(unittest.TestCase):
    """
    Unittest class for testing the function analyze_message in message_handler.py
    """
    def test_am_00_correct_request(self):
        """
        Positive test with correct formatting in a message
        """
        input_text = "#bot bodyshaming https://t.co/0815"
        expected_result = {"found_match": True,
                           "message": "bodyshaming",
                           "short_url": "https://t.co/0815"}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "Match found expected with message and tweet-url.")

    def test_am_01_wrong_key_sign(self):
        """
        Negative test with wrong key word
        """
        input_text = "!bot bodyshaming https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because wrong command found.")

    def test_am_02_only_message_and_url(self):
        """
        Negative test with only message and url and no keyword
        """
        input_text = "bodyshaming https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because no command found.")

    def test_am_03_only_message(self):
        """
        Negative test with only a message and no url or keyword
        """
        input_text = "bodyshaming"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only message.")

    def test_am_04_only_url(self):
        """
        Negative test with only url and no message or keyword
        """
        input_text = "https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only url.")

    def test_am_05_only_command(self):
        """
        Negative test with only keyword and no message or url
        """
        input_text = "#bot"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command.")

    def test_am_06_command_and_text(self):
        """
        Negative test with keyword and message but no url
        """
        input_text = "#bot hallo"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and message.")

    def test_am_07_command_and_url(self):
        """
        Negative test with keyword and url but no message
        """
        input_text = "#bot https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and url.")

    def test_am_08_nothing(self):
        """
        Negative test with empty message
        """
        input_text = " "
        expected_result = {"found_match": False,
                           "message": None,
                           "short_url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and url.")


class DecomposeTweetUrl(unittest.TestCase):
    """
    Unittest class for testing the function decompose_tweet_url in message_handler.py
    """
    def test_dtu_00_correct_request(self):
        """
        Positive test with correct tweet-url
        """
        input_url = "https://twitter.com/user0815/status/08157770815"
        expected_result = {"found_match": True,
                           "twitter_user_name": "user0815",
                           "tweet_id": "08157770815"}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "Match found expected with user name and tweet-id.")

    def test_dtu_01_wrong_start(self):
        """
        negative test with wrong url pattern at the beginning
        """
        input_url = "http://twitter.com/user0815/status/08157770815"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url start.")

    def test_dtu_02_wrong_end(self):
        """
        negative test with wrong url pattern at the end
        """
        input_url = "https://twitter.com/user0815/status/08157770815/d"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url end.")

    def test_dtu_03_wrong_mid(self):
        """
        negative test with wrong url pattern in the middle
        """
        input_url = "https://twitter.com/user0815/wrong/08157770815"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url mid.")


class ExtractExpandUrl(unittest.TestCase):
    """
    Unittest class for testing the function extract_expand_url in message_handler.py
    """
    def test_eeu_00_correct_request(self):
        """
        Positive test with correct tweet-expand_url
        """
        content = {"text": "#bot hello https://t.co/rEy33Np1N8",
                   "entities": {"hashtags": [{"text": "bot", "indices": [0, 4]}],
                                "user_mentions": [],
                                "urls": [{"url": "https://t.co/rEy33Np1N8",
                                          "expanded_url": "https://twitter.com/../status/0815",
                                          "display_url": "twitter.com/..",
                                          "indices": [36, 59]}]}}
        expected_result = "https://twitter.com/../status/0815"
        self.assertEqual(extract_expand_url(content), expected_result,
                         "Return expanded url")

    def test_eeu_01_wrong_dict(self):
        """
        Negative test with key error
        """
        content = {"text": "#bot hello https://t.co/rEy33Np1N8",
                   "entities": {"hashtags": [{"text": "bot", "indices": [0, 4]}],
                                "user_mentions": [],
                                "urlws": [{"url": "https://t.co/rEy33Np1N8",
                                           "expanded_url": "https://twitter.com/../status/0815",
                                           "display_url": "twitter.com/..",
                                           "indices": [36, 59]}]}}
        expected_result = ""
        self.assertEqual(extract_expand_url(content), expected_result,
                         "Dictionary has changed and key is not available.")

    def test_eeu_02_wrong_index(self):
        """
        Negative test with index error
        """
        content = {"text": "#bot hello https://t.co/rEy33Np1N8",
                   "entities": {"hashtags": [{"text": "bot", "indices": [0, 4]}],
                                "user_mentions": [],
                                "urlws": {"url": "https://t.co/rEy33Np1N8",
                                           "expanded_url": "https://twitter.com/../status/0815",
                                           "display_url": "twitter.com/..",
                                           "indices": [36, 59]}}}
        expected_result = ""
        self.assertEqual(extract_expand_url(content), expected_result,
                         "Dictionary has changed and list is not available.")


def run_some_tests():
    """
    Run function to collect all needed test in a suit and runs
    """
    test_classes_to_run = [AnalyzeMessageTest, DecomposeTweetUrl, ExtractExpandUrl]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    _ = runner.run(big_suite)


if __name__ == '__main__':
    run_some_tests()
