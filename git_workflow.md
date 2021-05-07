
# Git workflow

This repository uses the *Git Flow* workflow. Assuming the `git-flow` plugin is installed, you can 
setup your repository as follows:

```bash
# Initialize the git-glow plugin
$ git flow init

Which branch should be used for bringing forth production releases?
   - develop
   - feature/flask-migrate-sample-data
# ==> Use branch "master" for releases
Branch name for production releases: [] master
# ==> Use branch "develop" for next 
Which branch should be used for integration of the "next release"?
   - develop
Branch name for "next release" development: [develop]

How to name your supporting branch prefixes?
Feature branches? [feature/]
Bugfix branches? [bugfix/]
Release branches? [release/]
Hotfix branches? [hotfix/]
Support branches? [support/]
# ==> Use "v" as tag prefix
Version tag prefix? [] v
# ==> Use the default hooks path, it is usually OK
Hooks and filters directory? [path_to_the_repo/intranet/.git/hooks]
```
