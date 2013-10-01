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

from pyjenkins import Jenkins, Job, Build
from pyjenkins.jenkins import JobSummary, BuildSummary
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


class TestJob(RequestMockMixin, unittest.TestCase):
    def setUp(self):
        self.test_data = {
            'description': 'A test job',
            'displayName': 'Test Job',
            'url': 'http://example.com/test-job',
            'builds': [],
            'color': 'blue',
            'inQueue': False,
            'healthReport': [],
            'nextBuildNumber': 1
        }

    @patch('pyjenkins.jenkins.requests')
    def test_job_init(self, requests):
        self.setup_response(requests, self.test_data)
        job = Job('http://example.com/test-job')
        self.assertEqual(len(job.build_summaries), 0)
        self.assertEqual('blue', job.color)

    @patch('pyjenkins.jenkins.requests')
    def test_get_job_from_summary(self, requests):
        self.setup_response(requests, self.test_data)
        summary = JobSummary(name='Test Job',
                             url='http://example.com/test-job',
                             color='blue')
        job = summary.get_job()
        self.assertEqual(len(job.build_summaries), 0)
        self.assertEqual('blue', job.color)

    @patch('pyjenkins.jenkins.requests')
    def test_list_build_summaries(self, requests):
        self.test_data['builds'] = [
            {'url': 'http://example.com/test-job/1', 'number': '1'},
            {'url': 'http://example.com/test-job/2', 'number': '2'},
            {'url': 'http://example.com/test-job/3', 'number': '3'},
        ]
        self.setup_response(requests, self.test_data)
        job = Job('http://example.com/test-job')
        self.assertEqual(len(job.build_summaries), 3)
        build1 = job.build_summaries[0]
        self.assertEqual(type(build1), BuildSummary)


class TestBuild(RequestMockMixin, unittest.TestCase):
    def setUp(self):
        self.test_data = {
            'result': 'SUCCESS',
            'building': False,
            'id': '1234-5678-9',
            'number': 1,
            'estimatedDuration': 60000,
            'duration': 60100,
            'actions': [],
        }

    @patch('pyjenkins.jenkins.requests')
    def test_build_init(self, requests):
        self.setup_response(requests, self.test_data)
        build = Build('http://example.com/test-job/1')
        self.assertEqual(build.started, True)
        self.assertEqual(build.complete, True)
        self.assertEqual(build.duration, 60100)
        self.assertEqual(build.estimated_duration, 60000)
        self.assertEqual(build.number, 1)
        self.assertEqual(build.successful, True)

    @patch('pyjenkins.jenkins.requests')
    def test_trigger_build_initial_404_response(self, requests):
        self.setup_response(requests, {}, response_ok=False,
                            response_status_code=404)
        build = Build.get_build('http://example.com/test-job', 1)
        self.assertEqual(build.started, False)

    @patch('pyjenkins.jenkins.requests')
    def test_build_refresh(self, requests):
        self.setup_response(requests, {}, response_ok=False,
                            response_status_code=404)
        build = Build.get_build('http://example.com/test-job', 1)
        self.assertEqual(build.started, False)
        self.setup_response(requests, self.test_data)
        build.refresh()
        self.assertEqual(build.started, True)
        self.assertEqual(build.estimated_duration, 60000)

    @patch('pyjenkins.jenkins.requests')
    def test_get_build_from_summary(self, requests):
        self.setup_response(requests, self.test_data)
        summary = BuildSummary(number=1, url="http://example.com/test-job/1")
        build = summary.get_build()
        self.assertEqual(build.started, True)

    @patch('pyjenkins.jenkins.requests')
    def test_get_build_with_job_url_ending_in_slash(self, requests):
        self.setup_response(requests, self.test_data)
        build = Build.get_build('http://example.com/test-job/', 1)
        requests.get.assert_called_with(
            'http://example.com/test-job/1/api/json', auth=None
        )
        self.assertTrue(build.started)

    @patch('pyjenkins.jenkins.requests')
    def test_get_build_with_build_number_as_string(self, requests):
        self.setup_response(requests, self.test_data)
        build = Build.get_build('http://example.com/test-job', '1')
        requests.get.assert_called_with(
            'http://example.com/test-job/1/api/json', auth=None
        )
        self.assertTrue(build.started)

    @patch('pyjenkins.jenkins.requests')
    def test_get_build_with_build_number_as_string_and_slash_url(self, requests):
        self.setup_response(requests, self.test_data)
        build = Build.get_build('http://example.com/test-job/', '1')
        requests.get.assert_called_with(
            'http://example.com/test-job/1/api/json', auth=None
        )
        self.assertTrue(build.started)


if __name__ == '__main__':
    unittest.main()
