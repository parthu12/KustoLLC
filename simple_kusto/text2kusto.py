from flask import Flask, render_template, request
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from nl2query import KustoQuery
from azure.kusto.data.exceptions import KustoServiceError

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

def getColumns(database, table):
    columns = queryExecute(database, table + " | getschema ")
    return [x[0] for x in columns.primary_results[0]]

@app.route('/', methods=['GET', 'POST'])
def index():
    global KUSTO_CLIENT
    global SELECTED_DATABASE
    global SELECTED_TABLE
    global DATABASES
    global TABLES

    if request.method == 'POST':
        clusterName = request.form.get('clusterName')
        tenantID = request.form.get('tenantID')
        
        KUSTO_CLIENT = authenticate_toCluster(clusterName, tenantID)
        
        databases = getDatabaseList()
        DATABASES = databases
        SELECTED_DATABASE = None
        SELECTED_TABLE = None
        
        return render_template('index.html', databases=databases)

    elif request.method == 'GET':
        if request.form.get('database'):
            SELECTED_DATABASE = request.form.get('database')
            print("Selected database: " ,SELECTED_DATABASE)
            tables = getTableList(SELECTED_DATABASE)
            TABLES = tables
            return render_template('index.html', databases=DATABASES, tables=tables, selected_database=SELECTED_DATABASE)

        elif request.form.get('table'):
            SELECTED_TABLE = request.form.get('table')
            print("Selected table: " ,SELECTED_TABLE)
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE)

        elif request.form.get('prompt'):
            prompt = request.form.get('prompt')
            print("prompt: ", prompt)
            
            cols = getColumns(SELECTED_DATABASE, SELECTED_TABLE)
            kusto_query = queryGenerator(cols, SELECTED_TABLE, prompt)
            
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=kusto_query)

        elif request.form.get('query'):
            query = request.form.get('query')
            try :
                response = queryExecute(SELECTED_DATABASE, query)
            except KustoServiceError as error:
                print("error::::",error)
                return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=query,error = str(error))
            
            result = queryResponse(response)
            
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=query, result=result.to_html(classes='table table-striped'))

    return render_template('index.html')

@app.route('/action', methods=['GET', 'POST'])
def index1():
    global KUSTO_CLIENT
    global SELECTED_DATABASE
    global SELECTED_TABLE
    global DATABASES
    global TABLES
    global PROMPT

    if request.method == 'POST':
        if request.form.get('database'):
            SELECTED_DATABASE = request.form.get('database')
            print("Selected database: " ,SELECTED_DATABASE)
            tables = getTableList(SELECTED_DATABASE)
            TABLES = tables
            return render_template('index.html', databases=DATABASES, tables=tables,selected_database=SELECTED_DATABASE)

        elif request.form.get('table'):
            SELECTED_TABLE = request.form.get('table')
            print("Selected table: " ,SELECTED_TABLE)
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE)

        elif request.form.get('prompt'):
            prompt = request.form.get('prompt')
            print("prompt: ", prompt)
            PROMPT = prompt
            cols = getColumns(SELECTED_DATABASE, SELECTED_TABLE)
            kusto_query = queryGenerator(cols, SELECTED_TABLE, prompt)
            
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=kusto_query,prompt = PROMPT)

        elif request.form.get('query'):
            query = request.form.get('query')
            print("query: ", query)
            print("db: ", SELECTED_DATABASE)
            try :
                response = queryExecute(SELECTED_DATABASE, query)
            except KustoServiceError as error:
                print("error::::",error)
                return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=query,error = str(error))
            
            result = queryResponse(response)
            
            return render_template('index.html', databases=DATABASES, tables=TABLES, selected_database=SELECTED_DATABASE, selected_table=SELECTED_TABLE, query=query, prompt = PROMPT, result=result.to_html(classes='table table-striped'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
