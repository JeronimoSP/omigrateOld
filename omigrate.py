import xmlrpc.client
import openpyxl
import template
import pandas as pd
import rpcconnect

class Migrate:
    def __init__(self):
        self.source_system = None
        self.target_system = None

    def systemConnect(self, source_system, target_system):
        self.source_system = source_system
        self.target_system = target_system

        source_models, source_uid = self._create_client(self.source_system)
        source_version = source_models.execute_kw(self.source_system['db'], source_uid,
                                                  self.source_system['password'], 'ir.module.module', 'search_read',
                                                  [[('name', '=', 'base')]], {'fields': ['latest_version']})
        print("Connected to the source system. Version:", source_version)

        target_models, target_uid = self._create_client(self.target_system)
        target_version = target_models.execute_kw(self.target_system['db'], target_uid,
                                                  self.target_system['password'], 'ir.module.module', 'search_read',
                                                  [[('name', '=', 'base')]], {'fields': ['latest_version']})
        print("Connected to the target system. Version:", target_version)

    def dataTransfer(self, models):
        for model in models:
            self.dataExtraction(model)
            self.dataImport(model)

    def dataExtraction(self, model, folder):
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
        source_client, source_uid = self._create_client(self.source_system)
        target_client, target_uid = self._create_client(self.target_system)

        source_model_info = source_client.execute_kw(self.source_system['db'], source_uid,
                                                     self.source_system['password'], 'ir.model', 'search_read',
                                                     [[('model', '=', model)]])
        target_model_info = target_client.execute_kw(self.target_system['db'], target_uid,
                                                     self.target_system['password'], 'ir.model', 'search_read',
                                                     [[('model', '=', model)]])

        if source_model_info and target_model_info:
            # Model exists in both source and target systems
            source_model_fields = source_client.execute_kw(self.source_system['db'], source_uid,
                                                           self.source_system['password'], 'ir.model.fields',
                                                           'search_read',
                                                           [[('model_id', '=', source_model_info[0]['id'])]])
            target_model_fields = target_client.execute_kw(self.target_system['db'], target_uid,
                                                           self.target_system['password'], 'ir.model.fields',
                                                           'search_read',
                                                           [[('model_id', '=', target_model_info[0]['id'])]])

            # Create a new workbook
            workbook = openpyxl.Workbook()
            sheet = workbook.active

            # Write headers
            sheet['A1'] = 'Source System'
            sheet['B1'] = 'Target System'
            sheet['C1'] = 'is Present'
            sheet['D1'] = 'is Same Type'

            # Write total records count
            sheet['A2'] = f"Total Records: {len(source_model_fields)}"
            sheet['B2'] = f"Total Records: {len(target_model_fields)}"

            # Write unique users count
            source_users = set(field['create_uid'][1] for field in source_model_fields)
            target_users = set(field['create_uid'][1] for field in target_model_fields)
            sheet['A3'] = f"Unique Users: {len(source_users)}"
            sheet['B3'] = f"Unique Users: {len(target_users)}"

            # Write field details
            for i, field in enumerate(source_model_fields, start=4):
                sheet[f'A{i}'] = field['name']
                target_field = next((f for f in target_model_fields if f['name'] == field['name']), None)
                if target_field:
                    sheet[f'B{i}'] = target_field['name']
                    sheet[f'C{i}'] = True
                    sheet[f'D{i}'] = field['ttype'] == target_field['ttype']
                else:
                    sheet[f'B{i}'] = ''
                    sheet[f'C{i}'] = False
                    sheet[f'D{i}'] = False

            # Save the workbook
            workbook.save(f"{model}_comparison.xlsx")
            print(f"Comparison report for model '{model}' generated successfully.")
        else:
            print("Model does not exist in both source and target systems.")

    def _create_client(self, system):
        url = system['url'] + '/xmlrpc/2/common'
        common = xmlrpc.client.ServerProxy(url)
        uid = common.authenticate(system['db'], system['username'], system['password'], {})

        url = system['url'] + '/xmlrpc/2/object'
        models = xmlrpc.client.ServerProxy(url)
        return models, uid

# Example usage

migrate = Migrate()

migrate.source_system = rpcconnect.source_system
migrate.target_system = rpcconnect.target_system

print(migrate.source_system)
print(migrate.target_system)

migrate.systemConnect(migrate.source_system, migrate.target_system)

model_to_compare = 'res.partner'
migrate.modelCompare(model_to_compare)

# Rest of the code...
