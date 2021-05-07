
# DB management

## Create new revisions (versions, migrations)

**1. Run the following**

`flask db migrate`

**2. REVIEW, REVIEW, REVIEW!**

Review the newly created migration file (in `migrations/versions`)

## Upgrade or downgrade a DataBase

`flask db upgrade [revision]` and `flask db downgrade [revision]`

## Populate the DB with sample data

`flask db upgrade; flask populate`