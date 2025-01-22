
import boto3
import json
import os
import tempfile
import psycopg2
import psycopg2.extras
from botocore.exceptions import ClientError

def redshift_connection_by_arn(client):
    try:
        client_data = get_client_info(client)#is a way of storing secrets if needed we can store in csv file if the data is not important, if we want to secire store it in an environment variable
        arn_cluster_and_user = client_data.get('redshift_arn').split(':')[-1]
        cluster,db_user = arn_cluster_and_user.split('/')

        client = boto3.client('redshift')
        cluster_response = client.describe_clusters(ClusterIdentifier=cluster)
        
        db_host = cluster_response['Clusters'][0]['Endpoint']['Address']
        db_port = cluster_response['Clusters'][0]['Endpoint']['Port']
        
        credential_response = client.get_cluster_credentials(
            DbUser=db_user,
            DbName = client_data.get('database'),
            ClusterIdentifier=cluster)
        
        db_password = credential_response['DbPassword']
        db_user = credential_response['DbUser']
        connection = psycopg2.connect(dbname=client_data.get('database'), host=db_host , port= db_port, user= db_user, password= db_password)
        return connection

    except Exception as e:
        print(e)

def upsert_table(stg_table_name,redshift_table, s3_path, aws_access_key_id=None, aws_secret_access_key=None, aws_region=None):
    """
    Generate a Redshift SQL query to upsert data from an S3 bucket into a Redshift table.

    This function constructs an SQL query that:
    1. Drops any existing temporary staging table.
    2. Creates a new temporary staging table with the same structure as the target Redshift table.
    3. Copies data from the specified S3 path into the staging table.
    4. Identifies records in the staging table that do not exist in the target Redshift table.
    5. Deletes those records from the Redshift table.
    6. Inserts the new records into the Redshift table.

    Args:
        stg_table_name (str): The name of the temporary staging table to be created.
        redshift_table (str): The name of the target Redshift table to upsert data into.
        s3_path (str): The S3 path from which to copy data.
        aws_access_key_id (str, optional): AWS access key ID for S3 access. Defaults to None.
        aws_secret_access_key (str, optional): AWS secret access key for S3 access. Defaults to None.
        aws_region (str, optional): AWS region where the S3 bucket is located. Defaults to None.

    Returns:
        str: The SQL query as a string.

    Raises:
        Exception: If any error occurs while generating the SQL query.
    """
    try:
            query = f""" BEGIN TRANSACTION;
                DROP TABLE IF EXISTS {stg_table_name};
                CREATE TEMP TABLE {stg_table_name} (LIKE {redshift_table});

                COPY {stg_table_name} FROM '{s3_path}'
                ACCESS_KEY_ID '{aws_access_key_id}' SECRET_ACCESS_KEY '{aws_secret_access_key}'
                REGION '{aws_region}'
                FORMAT AS JSON 'auto' TIMEFORMAT 'epochsecs';

                DROP TABLE IF EXISTS records_to_update;
                CREATE TEMP TABLE records_to_update AS (
                    SELECT * FROM {stg_table_name}
                    MINUS 
                    SELECT * FROM {redshift_table}
                );

                DELETE FROM {redshift_table}
                USING records_to_update
                WHERE {redshift_table}.id = records_to_update.id
                AND {redshift_table}.object = records_to_update.object; 

                INSERT INTO {redshift_table}
                SELECT * FROM records_to_update;

                END TRANSACTION;
                """
            return query

    except Exception as error:
        print(f"An error occurred while generating the SQL query: {error}")
        raise

def copy_to_redshift(s3_path, tablename, arn=None, aws_access_key_id=None, aws_secret_access_key=None, aws_region=None, extra_toppings=None):
    try:
        query = f"""copy {tablename} from '{s3_path}'
            iam_role '{arn}'
            REGION {aws_region}
            format as json 'auto' timeformat 'epochsecs' ;"""
        return query

    except Exception as error:
        print(error)

def generate_temporary_file(list_data):
    
    try:
        temp_file = tempfile.TemporaryFile()
        for itm in list_data:
            json_data = json.dumps(itm)+'\n'
            temp_file.write(json_data.encode('utf-8'))
        temp_file.seek(0)
        print('temp file has been created')
        return temp_file

    except Exception as e:
        print(e)

def upload_fileobj_to_s3(data,
                        s3_filename,
                        s3_path,
                        bucket_name):
    ''' upload data to s3 '''
    try: 
        s3 = boto3.resource('s3')
        s3_path = os.path.join(s3_path,s3_filename)
        s3object = s3.Object(bucket_name, s3_path)
        s3object.put(
            Body=(bytes(json.dumps(data).encode('UTF-8')))
        )

        return True
    
    except FileNotFoundError:
        print("The S3 file was not found")
        return False

    except Exception as e:
        print(f"Error with S3 upload: {e}")
        return False

def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True

def read_file_from_s3(s3_bucket, s3_file_path):
    """
    reading the body of a file directly from S3
    :param s3_bucket: s3 bucket where the file is stored
    :param s3_file_path: absolute path of the file to read
    :return:
    """
    try:
        s3 = boto3.resource('s3')
        s3object = s3.Object(s3_bucket, s3_file_path)
        body = s3object.get()['Body'].read().decode("utf-8")
        return body

    except Exception as error:
        print(error)

def unload_to_s3(s3_path,inner_query, iam_role=None,aws_access_key_id=None,aws_secret_access_key=None,aws_region=None,extra_toppings=None):
    """
    
    s3_path: f"s3://{s3bucket}/{s3prefix}/{filename.csv}"
    extra_toppings: list
    """
    try:
        if not extra_toppings:
            extra_toppings=[]
        if iam_role:
            query = f"""UNLOAD ($$ {inner_query}$$)
                TO '{s3_path}'
                iam_role '{iam_role}' 
                parallel off
                {extra_toppings}"""
        else:
            query = f""" unload(
                $$ {inner_query} $$)
                to '{s3_path}' 
                access_key_id '{aws_access_key_id}'
                secret_access_key '{aws_secret_access_key}'
                REGION '{aws_region}'
                parallel off
                {extra_toppings};
            """
        return query
    except Exception as e:
        print(e)