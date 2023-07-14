import rpcconnect

# Test RPC connection using source_system
source_url = rpcconnect.source_system['url']
source_db = rpcconnect.source_system['database']
source_username = rpcconnect.source_system['username']
source_password = rpcconnect.source_system['password']

# Create a test RPC connection using source_system
source_connection = xmlrpc.client.ServerProxy(source_url + '/xmlrpc/2/common')
source_uid = source_connection.authenticate(source_db, source_username, source_password, {})

# Test RPC connection using target_system
target_url = rpcconnect.target_system['url']
target_db = rpcconnect.target_system['database']
target_username = rpcconnect.target_system['username']
target_password = rpcconnect.target_system['password']

# Create a test RPC connection using target_system
target_connection = xmlrpc.client.ServerProxy(target_url + '/xmlrpc/2/common')
target_uid = target_connection.authenticate(target_db, target_username, target_password, {})

# Print the source and target system connection details
print("Source System Connection:")
print("URL:", source_url)
print("Database:", source_db)
print("Username:", source_username)
print("Password:", source_password)
print("Source System UID:", source_uid)

print("Target System Connection:")
print("URL:", target_url)
print("Database:", target_db)
print("Username:", target_username)
print("Password:", target_password)
print("Target System UID:", target_uid)
