from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table
from nl2query import KustoQuery
import streamlit as st

AAD_TENANT_ID = "0eadb77e-42dc-47f8-bbe3-ec2395e0712c"
KUSTO_CLUSTER = "https://help.kusto.windows.net/"

st.write(""" Enter your cluster url and tenantID """)
clusterName = st.text_input("cluster url")
tenantID = st.text_input("tenantID")
submit = st.button("submit")



def authenticate_toCluster(clusterName, tenantID):
    """Authenticates to the cluster using AAD device code flow"""
    KCSB = KustoConnectionStringBuilder.with_aad_device_authentication(
        clusterName)
    KCSB.authority_id = tenantID
    return KustoClient(KCSB)

def queryGenerator(cols, tableName, prompt):
    queryfier = KustoQuery(cols, tableName)
    return queryfier.generate_query(prompt)

def queryExecute(database, query):
    return KUSTO_CLIENT.execute(database, query)

def queryResponse(response):
    return dataframe_from_result_table(response.primary_results[0])

def getDatabase():
    database = queryExecute("", ".show databases | project DatabaseName")
    return queryResponse(database)

def getTables(database):
    tables = queryExecute(database, ".show tables | project TableName")
    return queryResponse(tables)

def getColumns(database, table):
    columns = queryExecute(database, table + " | getschema | project ColumnName")
    return queryResponse(columns)

if submit:
    
    KUSTO_CLIENT = authenticate_toCluster(KUSTO_CLUSTER, AAD_TENANT_ID)
    st.write(""" Choose your database name """)
    database = st.selectbox("database", getDatabase())
    print(database)
    st.write(""" Choose your table name """)
    submitted1 = st.form_submit_button(database)
    table = st.selectbox("table", getTables(database))
    print(table)
    submitted2 = st.form_submit_button(table)
    st.write(""" use columns in query """)
    cols =  getColumns(database, table)
    print(cols)
    prompt = st.text_input("Enter a query")
    query = queryGenerator(cols, table, prompt)
    st.text(query)
    execute = st.button("execute")
    if execute:
        response = queryExecute(database, query)
        st.text(queryResponse(response))
        
