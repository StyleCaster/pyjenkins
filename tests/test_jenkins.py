#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jenkins
----------------------------------

Tests for `pyjenkins` module.
"""

import unittest

from pyjenkins import jenkins
from pyjenkins.jenkins import _get_json_api_url


class TestGetJsonApiUrl(unittest.TestCase):
    def test_url_transformation(self):
        # (input, expected_output)
        test_urls = (
            ('http://example.com', 'http://example.com/api/json'),
            ('http://example.com/', 'http://example.com/api/json'),
            ('http://example.com/api/json', 'http://example.com/api/json'),
            ('http://example.com/job/1', 'http://example.com/job/1/api/json'),
            ('http://example.com/job', 'http://example.com/job/api/json'),
        )
        for url, expected_output in test_urls:
            result = _get_json_api_url(url)
            msg = ("Tested {0}, expected {1}, got {2}".format(url,
                                                              expected_output,
                                                              result))
            self.assertEqual(expected_output, result, msg)


class TestJenkins(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
