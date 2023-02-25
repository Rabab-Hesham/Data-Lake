import configparser
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, date_format


config = configparser.ConfigParser()
config.read('dl.cfg')

os.environ['AWS_ACCESS_KEY_ID']=config['default']['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY']=config['default']['AWS_SECRET_ACCESS_KEY']



def create_spark_session():
    spark = SparkSession \
        .builder \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:2.7.0") \
        .getOrCreate()
    return spark



def process_song_data(spark, input_data, output_data):
    """
    Load data from song_data dataset and extract columns
    for songs and artist tables and write the data into parquet
    files which will be loaded on s3.
    Parameters
    spark: spark session that has been created
    input_data: path to the song_data s3 bucket.
    output_data: path where the parquet files will be written.
    """
     #get filepath to song data file
    song_data = input_data + 'song_data/A/A/A/*.json'
    
    # read song data file
    df = spark.read.json(song_data)
    

    # extract columns to create songs table
    songs_table = df.select('song_id', 'title', 'artist_id', 'duration', 'year').dropDuplicates(['song_id'])
    
    # write songs table to parquet files partitioned by year and artist
    songs_table.write.partitionBy("year", "artist_id").parquet(path = output_data + "/songs/songs.parquet", mode = "overwrite")


    # extract columns to create artists table
    artists_table = df.select('artist_id', 'artist_name', 'artist_location','artist_latitude','artist_longitude').dropDuplicates()
    
    # write artists table to parquet files
    artists_table.write.mode("overwrite").parquet(os.path.join(output_data, 'artists.parquet'))

def process_log_data(spark, input_data, output_data):
    """
    Load data from log_data dataset and extract columns
    for users and time tables, reads both the log_data and song_data
    datasets and extracts columns for songplays table with the data.
    It writes the data into parquet files which will be loaded on s3.
    Parameters
    spark: spark session that has been created
    input_data: path to the log_data s3 bucket.
    output_data: path where the parquet files will be written.
    """
     
    # get filepath to log data file
    log_data = input_data + 'log_data/*/*/*.json'


    # read log data file
    df = spark.read.json(log_data)
    
    # filter by actions for song plays
    df = df.where(df.page == 'NextSong')

    # extract columns for users table    
    users_table = df.select("userId", "firstName", "lastName", "gender", "level").distinct()
    
    # write users table to parquet files
    users_table.write.parquet(os.path.join(output_data, "users.parquet"), mode="overwrite")
    
    
    #create timestamp column from original timestamp column
    get_timestamp = udf(lambda x:  datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d %H:%M:%S'))
    df = df.withColumn("timestamp", get_timestamp(df.ts))

    
    # create datetime column from original timestamp column
    get_datetime = udf(lambda x: datetime.fromtimestamp(x/1000).strftime('%Y-%m-%d'))
    df = df.withColumn("datetime", get_datetime(df.ts))
    
    # extract columns to create time table

    dayofweek = udf(lambda x: (datetime.strptime(x, '%Y-%m-%d').strftime('%w')))
    time_table = df.select('datetime') \
                           .withColumn('start_time', df.datetime) \
                           .withColumn('hour', hour('datetime')) \
                           .withColumn('day', dayofmonth('datetime')) \
                           .withColumn('week', weekofyear('datetime')) \
                           .withColumn('month', month('datetime')) \
                           .withColumn('year', year('datetime')) \
                           .withColumn('weekday', dayofweek('datetime')) \
                           .dropDuplicates()

    
    # write time table to parquet files partitioned by year and month
    time_table.write.partitionBy('year', 'month').mode('overwrite').parquet(output_data + '/time/time_table.parquet')
    

    # read in song data to use for songplays table
    song_df = spark.read.json(input_data + 'song_data/A/A/A/*.json')

    # extract columns from joined song and log datasets to create songplays table 
    songplays_table = df.join(song_df, (df.song == song_df.title) &  \
                              (df.artist == song_df.artist_name) &  \
                              (df.length == song_df.duration), 'left_outer').select(\
            df.timestamp,
            col("userId").alias('user_id'),
            df.level,
            song_df.song_id,
            song_df.artist_id,
            col("sessionId").alias("session_id"),
            df.location,
            col("useragent").alias("user_agent"),
            year('datetime').alias('year'),
            month('datetime').alias('month'))
    

    # write songplays table to parquet files partitioned by year and month
    songplays_table.write.partitionBy('year', 'month').mode('overwrite').parquet(output_data + 'songplays.parquet')



def main():
    spark = create_spark_session()
    input_data = "s3a://udacity-dend/"
    output_data = "s3a://aws-logs-431524077301-us-west-2/elasticmapreduce/"

    
                                
    process_song_data(spark, input_data, output_data)    
    process_log_data(spark, input_data, output_data)


if __name__ == "__main__":
    main()
