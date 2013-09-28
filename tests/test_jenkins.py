#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jenkins
----------------------------------

Tests for `pyjenkins` module.
"""

import unittest
import json

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from pyjenkins import Jenkins
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


class RequestMockMixin(object):
    def setup_response(self, mock, response_data, response_ok=True,
                       response_status_code=200):
        """
        Sets up the desired response from a requests mock object.
        Currently only supports GET requests.

        ``mock``: A requests mock object
        ``response_data``: The desired response as a Python dict
        ``response_ok``: The desired return value of response.ok.
                         Defaults to True
        ``response_status_code``: The desired return value of
                                  response.status_code. Defaults to
                                  200.
        """
        response = mock.get.return_value
        response.ok = response_ok
        response.status_code = response_status_code
        response.text = json.dumps(response_data)


class TestJenkins(RequestMockMixin, unittest.TestCase):

    def setUp(self):
        pass

    @patch('pyjenkins.jenkins.requests')
    def test_missing_password(self, requests):
        with self.assertRaises(AttributeError):
            jenks = Jenkins("http://example.com", 'username')

    @patch('pyjenkins.jenkins.requests')
    def test_missing_username(self, requests):
        with self.assertRaises(AttributeError):
            jenks = Jenkins('http://example.com', password='password')

    @patch('pyjenkins.jenkins.requests')
    def test_jenkins_init(self, requests):
        test_data = {
            'jobs': [
                {
                    'name': 'Test Job One',
                    'url': 'http://example.com/job1',
                    'color': 'blue'
                }
            ]
        }
        self.setup_response(requests, test_data)
        jenks = Jenkins("http://example.com")
        self.assertEqual(len(jenks.job_summaries), 1)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
