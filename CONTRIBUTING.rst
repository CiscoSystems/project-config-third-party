=============================================
How to contribute to the Cisco Third Party CI
=============================================

.. contents::
  :depth: 1

Introduction
------------

There are several steps required to contribute to the Cisco Third Party CI,
such as adding a new job or modifying an existing one.

This repo's master branch is the production CI and holds the stable version of
each of the jobs as well and the configuration about which jobs to run and
when.

In order to prevent any collateral damage to the stable running CI jobs
development and experimental jobs should be developed in a separate branch and
then pulled into the master branch and enabled on the check queue once they
have proven that they are stable.

To enforce this behaviour no changes can be pushed directly into the master
branch, therefore they must go through a pull request process and be reviewed
before being accepted.

To allow the testing of in-development/experimental jobs running in the real CI
system, there is a separate Zuul queue provided which will only trigger a run
when a "cisco-experimental" is left as a comment on a gerrit patch. By default
this experimental queue will run the exact same code as the normal check job
queue however, by including a line ``Cisco-CI-Experimental-Branch: <branch>``
in the commit message of the gerrit patch it will allow you to run the code
from your development branch.

Typical workflow for adding a new job to the CI
-----------------------------------------------

When new jobs are added to the CI, they must first go through an experimental
phase to prove their success and stablity. These steps cover the processes
required to add a new experimental job, develop it and then get it promoted to
a regular job.

.. contents::
  :depth: 1
  :local:

Add a new job as an experimental job for development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Clone project-config-third-party to your local system

#. Create the first development branch by running ``git checkout -b <branch
   name>`` whist on ``master``, a good example of a branch name is
   ``adding_experimental_<job name>``

#. Define a new job and enable it in the experimental queue

   #. Modify jenkins/jobs/projects.yaml and under the project your adding the
      job for add::

        - 'gate-{name}-dsvm-tempest-smoke-{job-name}-{zuul-branch}-{node}':
          job-name: <job-name>

      Where ``<job-name>`` is replaced with the name of the job you want to add,
      for example ``nexus``, ``ironic-cimc``.

   #. Modify zuul/layout.yaml and under the project your job is for add the job
      under the experimental header::

        experimental:
          - gate-networking-cisco-dsvm-tempest-smoke-nexus-pike-centos-7-2-node
          - <your fully expanded job name here>

      The job name included in this file needs to be fully expanded with all the
      parts of the name populated, for example the first job in the example
      above was filled in with this information:

      - ``{name}`` is now ``networking-cisco`` because its for the project
        networking-cisco,
      - ``{job-name}`` is the job-name, in this case ``nexus``,
      - ``{zuul-branch}`` is now ``pike`` as this job is going to test the pike
        release,
      - ``{node}`` is now ``centos-7-2-node`` as this job needs to run on a
        centos-7-2-node cluster

#. Run the local tox test suite using ``tox`` to ensure that you've defined
   your job correctly in both the jenkins config file and the zuul config file.

#. Commit these changes, to your branch and push this changes and your branch
   to the upstream repo.

#. Create a pull request on the github repo between your development branch and
   the master branch for the change you've just pushed indicating that the pull
   request is to add a new experimental job.

#. That change will get reviewed and merged into the master branch enabling
   your new job to run when you leave the "cisco-experimental" comment on a
   gerrit patch upstream.

#. To test your job is running, create a [DNM] (do not merge) test patch to the
   project that your job is going to run against, making sure to include the
   line ``Cisco-CI-Experimental-Branch: <branch>`` (where you replace
   ``<branch>`` with the name of the branch we created in the earlier step) in
   the commit message, for example: https://review.openstack.org/#/c/514312/

#. Leave a comment on that patch with the text ``cisco-experimental`` and it
   should trigger your patch to enter the experimental queue, and you can check
   that on the `Zuul Dashboard`_.

#. After some amount of time the experimental queue should post its results to
   your [DNM] patch. Your new experimental job will fail because we haven't
   populated the playbooks for job yet.

Develop the job logic and test actions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Create a second development branch based on the first development branch by
   running ``git checkout -b <branch name>``, a good example branch name is
   ``adding_<job name>_job_logic``

#. Create the three base playbooks required for any job running the Cisco CI in
   the ``playbooks`` directory:

   - <job-name>-job-pre.yaml
   - <job-name>-job.yaml
   - <job-name>-job-post.yaml

#. Start populating the playbooks with roles from the ``playbooks/roles``
   directory to setup to perform the actions required by the job, the
   ``nexus-job-*.yaml`` are a good example of a job that requires some shared
   resources, and runs devstack + the tempest smoke tests.

#. Once you are happy you're ready to test your playbooks, run the ``tox -e
   linters`` command to validate your playbooks yaml syntax.

#. Then as a new commit to your development branch push your changes up to the
   upstream reposistory.

#. To test your changes return to your [DNM] patch on gerrit, and leave the
   ``cisco-experimental`` comment again, this time the CI will run all the jobs
   in the experimental queue with the changes you've made to your playbooks and
   any roles.

#. Wait for the results to be posted to the gerrit patch, and then check if all
   the jobs in the experimental queue have succeeded or failed.

#. If your job has failed you can view the logs by clicking the link posted by
   the CI system to gerrit.

#. If a job which isn't failing on the check queue is failing on your
   experimental run, it is likely your changes have had a side effect on
   another job and this will need repairing before your new job can be
   accepted.

#. Repeat the above steps to make any changes you need to make to the playbooks
   or roles until they are testing what they should be testing and all the jobs
   that are already in the check queue are also passing along side your new
   job. There may be other experimental jobs in the queue that are failing, but
   you can ignore those.

.. note::

  Remember to rebase your changes on to master regularly by running ``git fetch
  && git rebase -i origin/master`` so that your branch remains up to date with
  the current stable state of the repository.

Get your new job accepted into the master branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Do a final rebase on to master by running ``git fetch && git rebase -i
   origin/master``, if there are any conflicts resolve them.

#. Make a change in ``zuul/layout.yaml``, to additionally add your job/jobs
   into the check queue::

     check:
       - gate-networking-cisco-dsvm-tempest-smoke-nexus-pike-centos-7-2-node
       - <your fully expanded job name here>

#. Ensure that your code is passing all the linters by running ``tox`` and fix
   any issues.

#. Ensure all your logic is commited and your branch is pushed up to the
   upstream repo.

#. Go to the [DNM] gerrit patch and issue one final ``cisco-experimental``
   comment to run the job in its current state.

#. Create a new pull request from your branch to the master branch, indicating
   that you are promoting your job to a check job, and in the description add a
   link to the gerrit patch with the successfully passing experimental results.

#. This pull request will then be reviewed and if there are no issues found
   with it, it'll be accepted and merged onto the master branch.

.. note::

  If a pull request is merged and results in consistent failures then that
  commit will be reverted to restore the CI to working order. The issue can
  then be fixed on your development branch and a new pull request made to
  reaccept your job.

Typical workflow for modifying an existing CI job
-------------------------------------------------

Occasionally an existing job in the CI will need updating to increase its
feature coverage or to repair it after an external action causes it to fail
regularly. The process for repairing these jobs is similar to the process for
adding a new job except that there is no need to add a new experimental job, as
this job should already be running in the experimental queue. These steps cover
the processes required to update and test an existing job, and then get the fix
for that job accepted into the master branch.

.. contents::
  :local:

Develop the fix for the job logic and test it
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Clone project-config-third-party to your local system

#. Create a new development branch by running ``git checkout -b <branch name>``

#. To test the fixes you've made to the job, create a [DNM] (do not merge) test
   patch to the project that your job is running against, making sure to
   include the line ``Cisco-CI-Experimental-Branch: <branch>`` (where you
   replace ``<branch>`` with the name of the branch we created in the earlier
   step) in the commit message, for example:
   https://review.openstack.org/#/c/514312/

#. Make the required changes to the playbooks and roles for the job that needs
   fixing.

#. Commit and push the branch with your changes back to the
   project-config-third-party repo.

#. Leave a comment on your [DMN] patch with the text ``cisco-experimental`` and
   it should trigger your patch to enter the experimental queue, and you can
   check that on the `Zuul Dashboard`_.

#. Wait for the results to be posted to the gerrit patch, and then check if all
   the jobs in the experimental queue have succeeded or failed.

#. If the job has failed you can view the logs by clicking the link posted by
   the CI system to gerrit.

#. If a job which isn't failing on the check queue is failing on your
   experimental run, it is likely your changes have had a side effect on
   another job and this will need repairing before your new job can be
   accepted.

#. Repeat the above steps to make any changes you need to make to the playbooks
   or roles until they are testing what they should be testing and all the jobs
   that are already in the check queue are also passing along side with the job
   you are fixing There may be other experimental jobs in the queue that are
   failing, but you can ignore those.

.. note::

  If a patch set is already in the cisco-experimental queue leaving another
  ``cisco-experimental`` comment will **NOT** cause that job to restart. If you
  notice an intermittent error and want to restart the experimental queue run
  the best option is to rebase and submit another patch set to your [DNM]
  patch, as new patch sets will clear all previous jobs from the queue.

Get your fix accepted into the master branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Do a final rebase on to master by running ``git fetch && git rebase -i
   origin/master``, if there are any conflicts resolve them.

#. Ensure that your code is passing all the linters by running ``tox`` and fix
   any issues.

#. Ensure all your logic is commited and your branch is pushed up to the
   upstream repo.

#. Go to the [DNM] gerrit patch and issue one final ``cisco-experimental``
   comment to run the job in its current state.

#. Create a new pull request from your branch to the master branch, indicating
   that you are promoting your job to a check job, and in the description add a
   link to the gerrit patch with the successfully passing experimental results.

#. This pull request will then be reviewed and if there are no issues found
   with it, it'll be accepted and merged onto the master branch.

.. _Zuul Dashboard: http://3ci-zuul.ciscolabs.net

Only run a subset of tests in the experimental queue
----------------------------------------------------

While developing new jobs or modifying existing ones it is recommended to only
run the tests you are creating/modifying in the experimental queue in order to
speed up test run times and reduce load on the CI.

To do this you can add a regex pattern to the commit message of your [DNM]
patch on gerrit to tell the third party CI to only run certain jobs. In your
commit message add the line ``Cisco-CI-Experimental-Regex: <regex-pattern>``
(where <regex-pattern> matches the jobs you want to run). An example can be
seen - https://review.openstack.org/#/c/542324/

Common examples:

- Only run ASR1K - ``Cisco-CI-Experimental-Regex: .*-asr1k-.*``
- Only run UCSM - ``Cisco-CI-Experimental-Regex: .*-ucsm-.*``
- Only run Nexus - ``Cisco-CI-Experimental-Regex: .*-nexus-.*``

With the regex applied the "skipped" jobs will show up as "failed" in the
results, and it is expected that at least one final run with all the jobs
enabled is run before we merge the changes to project-config-third-party to
ensure there are no regressions in the other jobs caused by the changes.
