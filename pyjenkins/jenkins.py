#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from urlparse import urljoin

import requests

from .exceptions import APIError, DoesNotExist


class Struct:
    def __init__(self, **attrs):
        self.__dict__.update(attrs)


def _requests_get(url, auth=None):
    r = requests.get(url, auth=auth)
    if not r.ok:
        raise APIError("Jenkins API returned this error: {0}".format(r.reason))
    return json.loads(r.text)


def _get_json_api_url(url):
    """
    Take a Jenkins URL, and return the URL for the JSON API representation.
    """
    if url[-4:] == 'json':
        return url
    if url[-1:] != "/":
        url += "/"
    return urljoin(url, 'api/json')


class Jenkins(object):
    """
    Primary interface to a Jenkins instance.
    """
    def __init__(self, url, username=None, password=None):
        self._endpoint = _get_json_api_url(url)
        auth = None
        if username:
            if username and password:
                auth = (username, password)
            else:
                raise AttributeError("Username and password required.")
        self._auth = auth
        self._load_data()

    def __repr__(self):
        return "<Jenkins {0}>".format(self.url)

    def _load_data(self):
        data = _requests_get(self._endpoint, self._auth)
        self.job_summaries = [JobSummary(**kwargs)
                              for kwargs in data.get('jobs', [])]

    def get_job(self, job_summary):
        """
        Given a JobSummary, return a Job instance.
        """
        return Job(job_summary.url, auth=self._auth)

    def get_job_by_name(self, job_name):
        """
        Given a job name as a string, return a Job instance.

        Raises ``DoesNotExist`` if the requested job name can not be found.
        """
        for summary in self.job_summaries:
            if summary.name == job_name:
                return self.get_job(summary)
        raise DoesNotExist("Job {0} not found.".format(job_name))


class JobSummary(object):
    """
    Limited information about a job.
    """
    def __init__(self, name=None, url=None, color=None):
        if name is None or url is None or color is None:
            raise AttributeError("JobSummary missing required kwargs")
        self.name = name
        self.url = url
        self.color = color

    def __repr__(self):
        return "<JobSummary {0}>".format(self.name)


class Job(object):
    """
    Primary interface to a Jenkins job. Holds job status and metadata
    information, and can trigger a build.
    """
    def __init__(self, url, auth=None):
        self._endpoint = _get_json_api_url(url)
        self._auth = auth
        self._load_data()

    def __repr__(self):
        return "<Job {0}>".format(self.name)

    def build(self, token):
        """
        Trigger a build.

        Returns the expected build number.
        """
        # We need to be sure our next_build_number is correct, because
        # Jenkins doesn't return any useful info (like the build number)
        # when we trigger a build
        self._load_data()
        trigger_build_url = urljoin(self.url, 'build')
        response = requests.post(trigger_build_url, params={'token': token},
                                 auth=self._auth)
        if response.ok:
            return Build.get_build(self, self.next_build_number)

    def _load_data(self):
        data = _requests_get(self._endpoint, auth=self._auth)
        self.description = data.get('description')
        self.name = data.get('displayName')
        self.url = data.get('url')
        self._build_urls = data.get('builds', [])
        self.color = data.get('color')
        self._in_queue = data.get('inQueue', False)
        health_report = data.get('healthReport', [])
        if health_report:
            self.health_report = Struct(**health_report[0])
        else:
            self.health_report = None
        self._raw_data = data
        self._builds = data.get('builds', [])
        self.next_build_number = data.get('nextBuildNumber')
        self.build_summaries = [BuildSummary(**kwargs)
                                for kwargs in data.get('builds', [])]

    def get_build(self, build_summary):
        return Build(build_summary.url, auth=self._auth)


class BuildSummary(object):
    def __init__(self, number=None, url=None):
        if number is None or url is None:
            raise AttributeError("Cannot init a Build without url and number")
        self.url = url
        self.number = number

    def __repr__(self):
        return "<BuildSummary for Build {0}>".format(self.number)


class Build(object):
    """
    Primary interface to a particular build.
    """
    def __init__(self, url, auth=None):
        self._endpoint = _get_json_api_url(url)
        self._auth = auth
        self.number = None
        self._load_data()
        self.started = False
        self.successful = False
        self.complete = False

    def __repr__(self):
        return "<Build {0}>".format(self.number)

    @classmethod
    def get_build(cls, job, build_number):
        url = "{0}/{1}".format(job.url, build_number)
        return cls(url, auth=job._auth)

    def _get_builds_by_branch_name(self):
        # look for 'buildsByBranchName'
        if not hasattr(self, '_actions'):
            self._actions = []
        builds_by_branch_name = None
        for action in self._actions:
            if 'buildsByBranchName' in action:
                builds_by_branch_name = action['buildsByBranchName']
                continue
        return builds_by_branch_name

    def _load_data(self):
        response = requests.get(self._endpoint, auth=self._auth)
        if response.status_code == 404:
            return
        if not response.ok:
            raise APIError("Jenkins build endpoint error")
        data = json.loads(response.text)
        self.started = True
        self.result_text = data.get('result')
        if self.result_text == 'SUCCESS':
            self.successful = True
        self.building = data.get('building', False)
        self.complete = not self.building
        self.id = data.get('id')
        self.number = data.get('number')
        self.estimated_duration = data.get('estimatedDuration')
        self.duration = data.get('duration')
        self._actions = data.get('actions', [])

    def refresh(self):
        self._load_data()
