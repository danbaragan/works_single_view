# Works Single View

Reconcile data from multiple sources to create a single view of an entity, in this case, a musical work.
This prototype implementation does not keep all the different sources and reconciles at view time
but rather reconciles at import time into a 'best version so far'

Pro: the volume of data is smaller and easier to manipulate and search
Con: some information is lost; the heuristics to auto-detect what to keep is tricky

A better idea would be to keep various sources and also construct a cached single view.
Not done in this exercise.

Also, play around with docker, flask, peewee, postgres, nginx

##tl;dr

- Have docker
- `ln -s deploy.dev deploy`
- `docker-compose up -d`
- `docker-compose exec web pytest -vv`
- `docker cp deploy.dev/works_metadata.csv bmat_web:/home/web/instance/`
- `docker-compose exec web flask init-db`
- `docker-compose exec web flask import-csv -f instance/works_metadata.csv`

## Notes

### reconciliation
  The reconciliation is done:
  - favouring unicode string over ascii ones for same length
  - favouring newer unicode over older if very little change (for smae length)
  - favouring extension of information and not trimming (if a name has one additional word this version will be
  kept)

  The reconciliation is WIP for contributor names (only applied to work titles)

### auto imports
 - a cronjob could search a data volume for new csv files and import them during low load hours

### scale
 Due to indexes and updates (rather than keeping all info ever) this should scale better than O(N^2)
 somewhere around O(N\*logN)
 Caching will play a crucial role though. Especially if a solution that does not discard information is chosen.
 (very probable)

### API

- GET /works
- GET /works/\<iswc\>
- GET /export
- GET /import

The API under works is rest.
The import/export api is temporary and very schematic

### different environments
 The structure is such that prod/staging/dev are already separated by env variables
 The symlink `deploy` should point to proper prod variables and docker-compose.override.yml must be moved out of the way
 It is far from production, but it is not dev-only focused either.
 On every environment tests can be run, though on prod this would probably not make sense.