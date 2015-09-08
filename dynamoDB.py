__author__ = 'elisabethpaulson'
import boto.dynamodb

conn=boto.dynamodb.connect_to_region('us-west-2')

print conn

message_table_schema=conn.create_schema(
    hash_key_name='forum_name',
    hash_key_proto_value=str,
    range_key_name='subject',
    range_key_proto_value=str
)
#conn=boto.connect_dynamodb()
#myschema=conn.create_schema(hash_key_name='username',hash_key_proto_value='S')
#table=conn.create_table(name='users', schema=myschema, read_units=1, write_units=1)
#user_data={'name':'Orlando Karam', 'password':'abc123', 'email':'ok@ok.com'}
#user=table.new_item(hash_key='okaram', attrs=user_data)
#user.put()

table=conn.create_table(
    name='messages',
    schema=message_table_schema,
    read_units=1,
    write_units=1
)