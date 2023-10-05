from flask import Flask, render_template, request
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from nl2query import KustoQuery

app = Flask(__name__)

AAD_TENANT_ID = "0eadb77e-42dc-47f8-bbe3-ec2395e0712c"
KUSTO_CLUSTER = "https://help.kusto.windows.net/"
KUSTO_CLIENT = None
SELECTED_DATABASE = None
SELECTED_TABLE = None

def authenticate_toCluster(clusterName, tenantID):
    KCSB = KustoConnectionStringBuilder.with_aad_device_authentication(clusterName)
    KCSB.authority_id = tenantID
    return KustoClient(KCSB)

def queryGenerator(cols, tableName, prompt):
    queryfier = KustoQuery(cols, tableName)
    return queryfier.generate_query(prompt)

def queryExecute(database, query):
    return KUSTO_CLIENT.execute(database, query)

def queryResponse(response):
    return dataframe_from_result_table(response.primary_results[0])

def getDatabaseList():
    database_query = ".show databases | project DatabaseName"
    response = queryExecute("", database_query)
    return [row[0] for row in dataframe_from_result_table(response.primary_results[0]).itertuples(index=False)]

def getTableList(database):
    table_query = f".show tables | project TableName"
    response = queryExecute(database, table_query)
    return [row[0] for row in dataframe_from_result_table(response.primary_results[0]).itertuples(index=False)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    global KUSTO_CLIENT
    global SELECTED_DATABASE
    global SELECTED_TABLE

    clusterName = request.form.get('clusterName')
    tenantID = request.form.get('tenantID')
    
    KUSTO_CLIENT = authenticate_toCluster(clusterName, tenantID)
    
    databases = getDatabaseList()
    
    return render_template('select_database.html', databases=databases)

@app.route('/select_database', methods=['POST'])
def select_database():
    global SELECTED_DATABASE
    SELECTED_DATABASE = request.form.get('database')
    
    tables = getTableList(SELECTED_DATABASE)
    
    return render_template('select_table.html', tables=tables)

def getColumns(database, table):
    print("table",table)
    print("db",database)
    columns = queryExecute(database, table + " | getschema ")
    
    return [x[0] for x in columns.primary_results[0]]

@app.route('/select_table', methods=['POST'])
def select_table():
    global SELECTED_TABLE
    SELECTED_TABLE = request.form.get('table')
    
    return render_template('query_prompt.html')



@app.route('/generate_query', methods=['POST'])
def generate_query():
    prompt = request.form.get('prompt')
    
    cols = getColumns(SELECTED_DATABASE, SELECTED_TABLE)
    print("cols",cols)
    kusto_query = queryGenerator(cols, SELECTED_TABLE, prompt)
    print("generated query:::::::",kusto_query)
    return render_template('generated_query.html', query=kusto_query)

@app.route('/execute_query', methods=['POST'])
def execute_query():
    query = request.form.get('query')
    
    response = queryExecute(SELECTED_DATABASE, query)
    result = queryResponse(response)
    
    return render_template('query_results.html', query=query, result=result.to_html(classes='table table-striped'))


    
if __name__ == '__main__':
    app.run(debug=True)
