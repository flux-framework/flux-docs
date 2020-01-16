.. _contributing:

============
Contributing
============

The Flux Framework team welcomes all contributors for bug fixes, code improvements, new features, simplifications, documentation, and more. Please do not hesitate to `contact us <https://github.com/orgs/flux-framework/people>`_ with any questions or concerns.

This guide details how to contribute to `Flux Framework projects <https://github.com/flux-framework>`_ in a standardized and efficient manner. Our projects follow the Collective Code Construction Contract (`C4.1 <https://github.com/flux-framework/rfc/blob/master/spec_1.adoc>`_) which describes an optimal collaboration model for open source projects, based on the GitHub fork+pull model.

.. _pull-requests:

-------------
Pull Requests
-------------

Use a pull request (PR) toward a repository's master branch to propose your contribution, including the specific issue number your PR resolves. If you are planning significant code changes, or have any questions, please open an issue and reference it in your PR. To contribute to a Flux Framework project:

* `Fork <https://help.github.com/en/github/getting-started-with-github/fork-a-repo>`_ the project.
* `Clone <https://help.github.com/en/github/getting-started-with-github/fork-a-repo#keep-your-fork-synced>`_ your fork. ``git clone git@github.com:[username]/flux-framework/[project].git``
* Create a topic branch to contain your change. ``git checkout -b new_feature``
* Create feature or add fix, and add tests if possible.
* Make sure everything still passes ``make check``.
* Rebase your commits into meaningfully labeled, easily digestible chunks, ideally without errors.
* Push the branch to your GitHub repo. ``git push origin new_feature``
* Create a PR against flux-framework/[project] and describe what your change does and why you think it should be merged. List any outstanding "to do" items.
* Each PR will be subjected to automated tests under `travis-ci.org <https://travis-ci.org/>`_.

Please note that PRs should be rebased onto the master of the target repository, not merged from the master into your branch. PRs that are a work in progress should have `WIP:` prefix or `work-in-progress` label to avoid automerging by mergify.io.

.. _dev-guidelines:

--------------------
Developer Guidelines
--------------------

* Keep the code lean and as simple as possible.
* Keep the code general and reasonably efficient.
* Review other issues and PRs to ensure you are not duplicating effort.
* Update the appropriate `documentation <https://github.com/flux-framework/docs>`_ or open an `issue <https://github.com/flux-framework/docs/issues>`_ to do so.
* Adhere to the coding style guide. The components of Flux written in C follow the Kernighan & Ritchie coding style, with exceptions enumerated in `RFC 7 <https://github.com/flux-framework/rfc/blob/master/spec_7.adoc>`_. The components of Flux written in Python follow the `black code style <https://black.readthedocs.io/en/stable/the_black_code_style.html>`_.
* Commit etiquette:

  * Avoid merge commits.
  * Separate work so that each commit fixes one problem.
  * Use `subsystem:` prefix in commit titles.
  * Each commit should have a message with title and body as described in C4.1 (e.g., imperative phrasing).

For more details about C4.1, including commit requirements, see `RFC 1 <https://github.com/flux-framework/rfc/blob/master/spec_1.adoc>`.
