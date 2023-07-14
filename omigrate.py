import xmlrpc.client
import rpcconnect
import openpyxl
import template
import pandas as pd

class Migrate:
    def __init__(self):
        self.source_system = None
        self.target_system = None

    def systemConnect(self, source_connection, target_connection):
        self.source_system = source_connection
        self.target_system = target_connection

    def dataTransfer(self, models):
        for model in models:
            self.dataExtraction(model)
            self.dataImport(model)

    def dataExtraction(self, model):
        source_client = self._create_client(self.source_system)
        records = source_client.execute_kw(self.source_system['db'], source_client.uid, self.source_system['password'],
                                           model, 'search_read', [[]])
        df = pd.DataFrame(records)
        df.to_excel(f"{model}_data.xlsx", index=False)

    def dataTransform(self, model, field_type_mapping):
        # Implement your logic to change field types of a model
        pass

    def dataImport(self, model):
        target_client = self._create_client(self.target_system)
        df = pd.read_excel(f"{model}_data.xlsx")
        records = df.to_dict('records')
        target_client.execute_kw(self.target_system['db'], target_client.uid, self.target_system['password'],
                                 model, 'create', [records])

    def modelCompare(self, model):
        source_client = self._create_client(self.source_system)
        target_client = self._create_client(self.target_system)

        source_model_info = source_client.execute_kw(self.source_system['db'], source_client.uid,
                                                     self.source_system['password'], 'ir.model', 'search_read',
                                                     [[('model', '=', model)]])
        target_model_info = target_client.execute_kw(self.target_system['db'], target_client.uid,
                                                     self.target_system['password'], 'ir.model', 'search_read',
                                                     [[('model', '=', model)]])

        if source_model_info and target_model_info:
            # Model exists in both source and target systems
            source_model_fields = source_client.execute_kw(self.source_system['db'], source_client.uid,
                                                           self.source_system['password'], 'ir.model.fields',
                                                           'search_read', [[('model_id', '=', source_model_info[0]['id'])]])
            target_model_fields = target_client.execute_kw(self.target_system['db'], target_client.uid,
                                                           self.target_system['password'], 'ir.model.fields',
                                                           'search_read', [[('model_id', '=', target_model_info[0]['id'])]])

            print("Model exists in both source and target systems.")
            print("Source model fields:")
            for field in source_model_fields:
                print(field['name'])
            print("Target model fields:")
            for field in target_model_fields:
                print(field['name'])
        else:
            print("Model does not exist in both source and target systems.")

    def _create_client(self, system):
        url = system['url'] + '/xmlrpc/2/common'
        common = xmlrpc.client.ServerProxy(url)
        uid = common.authenticate(system['db'], system['username'], system['password'], {})
        url = system['url'] + '/xmlrpc/2/object'
        return xmlrpc.client.ServerProxy(url)

# Example usage
migrate = Migrate()

source_system_connection = {
    'url': 'http://source_system_url',
    'db': 'source_system_db',
    'username': 'source_system_username',
    'password': 'source_system_password'
}

target_system_connection = {
    'url': 'http://target_system_url',
    'db': 'target_system_db',
    'username': 'target_system_username',
    'password': 'target_system_password'
}

migrate.systemConnect(source_system_connection, target_system_connection)

models_to_transfer = ['model1', 'model2', 'model3']
migrate.dataTransfer(models_to_transfer)

model_to_compare = 'model1'
migrate.modelCompare(model_to_compare)


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

print("\nTarget System Connection:")
print("URL:", target_url)
print("Database:", target_db)
print("Username:", target_username)
print("Password:", target_password)
print("Target System UID:", target_uid)

# Create a Migrate object and invoke modelCompare method
migrate = Migrate(source_system, target_system, model)
migrate.modelCompare(source_models[0])

# Rest of the code...
