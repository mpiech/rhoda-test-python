# rhoda-test-python

Small Python sample app to experiment with RHODA (Red Hat OpenShift Database Access)

(This is a work in progress; there's not yet enough explanation of the data structure and/or sample data provided here to get you a fully running app, but you can at least see what the code looks like.)

## Running on OpenShift

    oc new-project rhoda-test-python
    oc new-build openshift/python:3.9-ubi8~https://github.com/mpiech/rhoda-test-python
    oc new-app rhoda-test-python \
       -e GMAPS_KEY="xxx" \
       -e ATLAS_HOST="xxx.yyy.mongodb.net" \
       -e ATLAS_USERNAME="atlas-db-user-xxx" \
       -e ATLAS_PASSWORD="xxx" \
       -e ATLAS_DB="xxx" \
       -e PGHOST="p.xxx.db.postgresbridge.com" \
       -e PGUSER="postgres" \
       -e PGPASSWORD="xxx" \
       -e PGDB="postgres"
    oc expose service/rhoda-test-python

You'll need a google maps API key, a SQL database on Crunchy Bridge and a MongoDB on Mongo Atlas (structure and sample data to be added here later).

## Running Locally

   flask run

## License

Copyright © 2022
