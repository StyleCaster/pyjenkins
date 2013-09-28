========
Usage
========
PyJenkins provides three primary objects:

 * ``Jenkins``: Represents your entire Jenkins installation. A Jenkins
                installation contains zero or more jobs.
 * ``Job``: Represents a particular job. This is usually the equivalent of a
            'project'. A ``Job`` can trigger builds.
 * ``Build``: Represents an individual build.


TL;DR
-----

::

    from pyjenkins import Jenkins
    jenkins = Jenkins('http://example.com', 'username', 'password')
    job = jenkins.get_job_by_name('my-job')
    build = job.build('authentication token')
    build.started
    # False
    # Wait a bit for the build to start
    build.refresh()
    build.started
    # True
    build.estimated_duration
    # returns estimated build duration in milliseconds. Wait this amount
    build.refresh()
    build.completed
    # True
    build.successful
    # True

Getting a Jenkins instance
--------------------------

First, import the ``Jenkins`` class::

    from pyjenkins import Jenkins

Instantiate ``Jenkins`` with your Jenkins installation URL. This should be the
same as the URL for your Jenkins dashboard::

    jenkins = Jenkins('http://example.com/')

Optionally, pass a username and password::

    jenkins = Jenkins('http://example.com', 'username', 'password')


Getting a Job instance
----------------------

If you have a ``Jenkins`` instance, you can list the available jobs::

    >>> jenkins.job_summaries
    [<JobSummary my-first-job>,
     <JobSummary my-second-job]

A ``JobSummary`` class only contains limited information about a job::

    >>> job_summary.name
    'my-first-job'
    >>> job_summary.url
    'http://example.com/my-first-job'
    >>> job_summary.color
    'blue'

To get a full ``Job`` instance, there are three options:

 * From a ``JobSummary``::

       >>> job = job_summary.get_job()

 * By name, from a ``Jenkins`` instance::

       >>> job = jenkins.get_job_by_name('my-first-job')

 * By url, directly from the Jenkins API::

       >>> from pyjenkins import Job
       >>> auth = ('username', 'password')  # optional
       >>> job = Job('http://example.com/my-first-job', auth=auth)


Starting a Build
----------------

In order to trigger a build, your Jenkins job must be configured to allow
scripts to trigger builds remotely. To do this, go to the 'configure' section
of your job. In the 'Build Triggers' section, check
'Trigger builds remotely (e.g., from scripts)'. In the 'Authentication Token'
section, enter a string that you wish to use as an authentication token. This
is essentially a 'password' for PyJenkins. Be sure to click 'Save' in your
Jenkins configuration page.

You can use a ``Job`` to trigger a build::

    >>> token = 'your auth token'
    >>> build = job.build(token)


When a build is first triggered, there is a waiting period before the build
actually starts. During this time, the Jenkins API will return a 404, so the
build instance only has very limited information.

To update the build instance against the Jenkins API, call ``refresh()``::

    >>> build.refresh()
    >>> build.started
    True

At this point, the ``Build`` contains an estimated build time::

    >>> build.estimated_duration
    60123  # milliseconds

You should wait at least ``build.estimated_duration`` milliseconds before
refreshing your build object. After refreshing the ``build``, you can check
``build.complete``::

	>>> build.refresh()
	>>> build.complete
	True

Check to see if the build was successful::

	>>> build.successful
	True


Example Usage
-------------
::

	>>> from pyjenkins import Jenkins

	>>> # username and password optional
	>>> jenkins = Jenkins('https://jenkins.example.com/', 'username', 'password')

	>>> # list available jobs
	>>> jenkins.job_summaries
	[<JobSummary my-project>,
	 <JobSummary my-other-project>]

	>>> # get a job instance
	>>> job = jenkins.get_job_by_name('my-project')

	or

	>>> job = jenkins.job_summaries[0].get_job()

	>>> # Trigger a build.
	>>> # The job must be configured with 'trigger builds remotely'
	>>> build = job.build('token string')

	>>> # builds take a bit to start. Call 'refresh()' to update from the API
	>>> build.started
	False
	>>> # wait a bit
	>>> build.refresh()
	>>> build.started()
	True
	>>> # how long will the build take (in milliseconds)?
	>>> build.estimated_duration
	60588
	...
	>>> build.refresh()
	>>> build.complete
	True
	>>> build.successful
	True
	>>> print("Yay!")
	Yay!


You can also access a Job directly, which will reduce the number of API calls.
Note that the authentication credentials are passed differently::

    from pyjenkins import Job
    auth = ('username', 'password')
    job = Job('http://example.com/my-job', auth=auth)


Similarly, you can directly access a Build::

    from pyjenkins import Build
    auth = ('username', 'password')
    build = Build('http://example.com/my-job/1', auth=auth)
