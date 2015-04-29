===================
Joulupukki FrontEnd
===================



Installation
============

::

    sudo apt-get install npm nodejs-legacy ruby ruby-sass
    git clone https://github.com/titilambert/joulupukki.git
    cd joulupukki web
    source dev_virtualenv
    npm install


Dev
===

Load our dev virtualenv :

::

    source dev_virtualenv

To compile css files run :

::

    grunt sass

To compile js files run :

::

    grunt uglify

If you wish to develop in a docker container, here is how to proceed (assuming
you already have docker installed) :

::

    curl http://localhost:8080/app

You must leave grunt running in the background to automatically compile css
and minify/compress js files when source code changes

::

    grunt




Coding style
============

This project conforms to JSLint coding style (http://github.com/douglascrockford/JSLint).
Run the linter as follows:

::

    grunt jslint

Tests
=====

AngularJS comes with Karma which is an automatic unit test runner.
While running, Karma automatically executes the tests when any js file changes.
To launch Karma :

::

    npm test

Launch
======

::

    npm start


Now, go on http://127.0.0.1:8000

Contributing
============

To contribute to this project, please fork the repo. Then do your commits (branch as you will)
and then open a pull-request to this repo's master branch.

::

    <fork this repo on github>
    git clone your-repo/joulupukki
    git checkout -b dev-new-feature-xx
    git commit ...
    git push origin dev-new-feature-xx
    <You can now open your pull-request to this repo's master>

Good practices before opening a pull request:

    - Run tests with `npm test`
    - Lint your .js files with `grunt jslint`
    - Make sure your directives are prefixed with `adg`
    - Make sure your controllers are suffixed with `Ctrl`
    - Resolve merge conflicts locally

