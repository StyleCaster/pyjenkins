========
Usage
========

To use Jenkins in a project::

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
