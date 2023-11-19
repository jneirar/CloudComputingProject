from boto3 import session

ACCESS_ID = 'DO0067GURQ328CC9JWZ7'
SECRET_KEY = 'FWdypjDZW9s/Y56MFb+db+9sEoiA3YhuSBTwZj/+Iug'

# Initiate session
session = session.Session()
client = session.client('s3',
                        region_name='nyc3',
                        endpoint_url='https://nyc3.digitaloceanspaces.com',
                        aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)

# Print out bucket names
response = client.list_buckets()
spaces = [space['Name'] for space in response['Buckets']]
print("Spaces List: %s" % spaces)

# print carpets and files of bucket spacekube
response = client.list_objects(Bucket='spacekube')
for content in response['Contents']:
    print(content['Key'])

