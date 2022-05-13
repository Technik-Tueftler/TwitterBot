#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from source.message_handler import analyze_message, decompose_tweet_url


class AnalyzeMessageTest(unittest.TestCase):

    def test_AM_00_correct_request(self):
        input_text = "#bot bodyshaming https://t.co/0815"
        expected_result = {"found_match": True,
                           "message": "bodyshaming",
                           "url": "https://t.co/0815"}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "Match found expected with message and tweet-url.")

    def test_AM_01_wrong_key_sign(self):
        input_text = "!bot bodyshaming https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because wrong command found.")

    def test_AM_02_only_message_and_url(self):
        input_text = "bodyshaming https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because no command found.")

    def test_AM_03_only_message(self):
        input_text = "bodyshaming"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only message.")

    def test_AM_04_only_url(self):
        input_text = "https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only url.")

    def test_AM_05_only_command(self):
        input_text = "#bot"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command.")

    def test_AM_06_command_and_text(self):
        input_text = "#bot hallo"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and message.")

    def test_AM_07_command_and_url(self):
        input_text = "#bot https://t.co/0815"
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and url.")

    def test_AM_08_nothing(self):
        input_text = " "
        expected_result = {"found_match": False,
                           "message": None,
                           "url": None}
        self.assertEqual(analyze_message(input_text),
                         expected_result,
                         "No match expected because only command and url.")


class DecomposeTweetUrl(unittest.TestCase):

    def test_DTU_00_correct_request(self):
        input_url = "https://twitter.com/user0815/status/08157770815"
        expected_result = {"found_match": True,
                           "twitter_user_name": "user0815",
                           "tweet_id": "08157770815"}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "Match found expected with user name and tweet-id.")

    def test_DTU_01_wrong_start(self):
        input_url = "http://twitter.com/user0815/status/08157770815"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url start.")

    def test_DTU_02_wrong_end(self):
        input_url = "https://twitter.com/user0815/status/08157770815/d"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url end.")

    def test_DTU_03_wrong_mid(self):
        input_url = "https://twitter.com/user0815/wrong/08157770815"
        expected_result = {"found_match": False,
                           "twitter_user_name": None,
                           "tweet_id": None}
        self.assertEqual(decompose_tweet_url(input_url),
                         expected_result,
                         "No match expected because with wrong url mid.")


def run_some_tests():
    test_classes_to_run = [AnalyzeMessageTest, DecomposeTweetUrl]

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
