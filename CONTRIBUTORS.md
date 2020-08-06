## Guidelines for Contribution:

### For Admins:

1. Make sure you have cloned this repository. If not, do so by using ``git clone https://github.com/BIDS-Apps/rsHRF.git``. Switch into this directory and make sure to be on the master branch.
2. Go to ``circleci.com``, log in / link your GitHub account and click on the top-left corner to switch organization to ``BIDS-Apps``
3. Follow the project ``rsHRF`` from the ``Add Project`` menu, 4th button from the top left.
4. If you feel that a significant change has been made to the App and that it is ready to be deployed and pushed to the users, open the ``VERSION`` file, change the number there to the version you want the App to ship with and save the file. It is advisable to follow [semantic-versioning](https://semver.org/).
5. Add all the changed files and the newly changed ``VERSION`` file by using ``git add`` on the cloned repository.
6. Write a commit message using ``git commit -m "release x.x.x"`` where ``x.x.x`` is the version that you wrote in the ``VERSION`` file.
7. Run ``git push origin master`` to push these commits on this repository.
8. Run ``git tag x.x.x`` where ``x.x.x`` is the version that you wrote in the ``VERSION`` file.
9. Run ``git push origin x.x.x`` where ``x.x.x`` is the version that you wrote in the ``VERSION`` file.
10. The ``circleCI`` system will trigger the deployment on both PyPI and DockerHub automatically. Please note that for the updated Docker Image to appear on the DockerHub, it takes about 30 mins to do so. The package on the PyPI is updated quickly though.

### For Users:

If you find an error / issue, please open them up on the issues page of this repository. Possibly with the error received and a sample code that can reproduce the issue.

### For Developers:

If you have an idea, please open up a new issue for the same.


If you have some code changes to push, please submit a pull request from your forked verion of this repository. One of the admins will get back to you shortly.
