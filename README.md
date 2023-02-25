## Sparkify - Data Lake

Sparkify,a music streaming startup, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

The goal of the project is building an ETL pipeline that extracts their data from S3, processes them using Spark, and loads the data back into S3 as a set of dimensional tables. This will allow their analytics team to continue finding insights in what songs their users are listening to.

## Datasets

The project consist of two datasets, of JSON format, that reside in S3. Here are the S3 links for each:

Song data: s3://udacity-dend/song_data
Log data: s3://udacity-dend/log_data

## Schema for Song Play Analysis

Using the song and log datasets, a star schema has been created that consist of 

# Fact Table
songplays - records in log data associated with song plays 
songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

# Dimension Tables
users - users in the app
user_id, first_name, last_name, gender, level

songs - songs in music database
song_id, title, artist_id, year, duration

artists - artists in music database
artist_id, name, location, lattitude, longitude

time - timestamps of records in songplays broken down into specific units
start_time, hour, day, week, month, year, weekday

# Files

etl.py : Python script to create the full pipeline.
README.md: The description of the project
dl.cfg : Config file for AWS access warehouse.
run.ipynb: to run the etl.py file local

# Run Instructions
1-Edit dl.cfg appropriately for your credentials.
2-Run etl.py to import the data from S3 JSON files and assembled the tables.
3-Query as needed.

