import azure.cosmos.cosmos_client as cosmos_client
import json

config = {
    'ENDPOINT': 'https://tohacks-sql.documents.azure.com:443/',
    'PRIMARYKEY': 'rVffuZftq16dKAIkAfsh81tdgo2UUjogYtpeSv0WtWGWWogovgjLKtlHBhkq1OKoLkmc5FV9UbpxfLv1hVhVUg==',
    'DATABASE': 'TOHacks Data',
    'CONTAINER': 'Options'
}
item1 = {
    'id': 'server1',
    'Web Site': 0,
    'Cloud Service': 0,
    'Virtual Machine': 0,
    'message': 'Hello World from Server 1!'
    }



# Initialize the Cosmos client
client = cosmos_client.CosmosClient(url_connection=config['ENDPOINT'], auth={
                                    'masterKey': config['PRIMARYKEY']})

database_link = 'dbs/' + 'TOHacks Data'
collection_link = database_link + '/colls/' + 'Options'

client.CreateItem(collection_link,item1)

print(client.ReadDatabase(database_link))
print(client.ReadContainer(collection_link))



# Query these items in SQL
query = {'query': 'SELECT * FROM server s'}

options = {}
options['enableCrossPartitionQuery'] = True
options['maxItemCount'] = 2

