`ln -s deploy.dev deploy`
`docker-compose up -d`
`docker cp deploy.dev/works_metadata.csv bmat_web:/home/web/instance/`
`docker-compose exec web flask import-csv -f instance/works_metadata.csv`
