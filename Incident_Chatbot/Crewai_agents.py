from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
import pyodbc

ELASTIC_HOST = "<your_elasticsearch_host>"
ELASTIC_PORT = 9200
ELASTIC_USERNAME = "<your_elasticsearch_username>"
ELASTIC_PASSWORD = "<your_elasticsearch_password>"
ELASTIC_CA_CERT = r"<path_to_elasticsearch_ca_cert>"
ELASTIC_INDEX = "incident_sop"


DB_CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=<your_server>;Database=<your_database>;Trusted_Connection=yes;'


def Multiagentsystem(user_query, user_query_with_context):
    """Function to handle multi-agent system for incident management queries"""
    process_flow = []
    
    llm = LLM(
        model="azure/gpt-4o",
        api_version="2025-01-01-preview",
        base_url="<your_azure_openai_endpoint>",
        api_key="<your_azure_openai_api_key>"
    )

    @tool
    def get_chunks_tool(query: str) -> str:
        """
        Retrieves relevant document chunks from Elasticsearch based on semantic similarity.
        
        Args:
            query: The search query string
            
        Returns:
            A formatted string containing the most relevant document chunks
        """
        try:
            # Track step - Incident_SOP_agent executing get_chunks_tool
            process_flow.append({
                "step_number": 1,
                "agent": "Manager Agent",
                "action": "Analyzing user question",
                "description": f"Analyzing query: {user_query}"
            })
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Manager Agent",
                "action": "Delegating to Incident_SOP_Agent",
                "description": f"Routing query to Incident_SOP_Agent"
            })

            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_SOP_Agent",
                "action": "Connecting to MCP ElasticSearch Sever",
                "description": f"Elastablishing connection"
            })

            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_SOP_Agent",
                "action": "Invoking get_chunks_tool",
                "description": f"Searching SOP documentation for: {query}"
            })


        
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            query_embedding = model.encode(query).tolist()
            
            
            es = Elasticsearch(
                hosts=[f"https://{ELASTIC_HOST}:{ELASTIC_PORT}"],
                basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                ca_certs=ELASTIC_CA_CERT,
                verify_certs=True
            )
            
            
            search_body = {
                "knn": {
                    "field": "content_embedding",
                    "query_vector": query_embedding,
                    "k": 5,
                    "num_candidates": 100
                },
                "fields": ["content", "chunk_id", "source"],
                "_source": ["content", "chunk_id", "source"]
            }
            
            results = es.search(index=ELASTIC_INDEX, body=search_body)
            
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_SOP_Agent",
                "action": "Processing search results",
                "description": f"Retrieved {len(results['hits']['hits'])} relevant document chunks"
            })
            
            # Step 4: Format and return results
            if results['hits']['total']['value'] == 0:
                return "No relevant chunks found for the query."
            
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_SOP_Agent",
                "action": "Formatting final response",
                "description": "Structuring retrieved chunks for presentation"
            })
            
            formatted_results = "Retrieved Document Chunks:\n" + "="*80 + "\n\n"
            
            for idx, hit in enumerate(results['hits']['hits'], 1):
                source = hit['_source']
                formatted_results += f"Chunk {idx}:\n"
                formatted_results += f"Content:\n{source.get('content', 'No content')}\n"
                formatted_results += "-"*80 + "\n\n"
            return formatted_results
            
        except Exception as e:
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_SOP_Agent",
                "action": "Error in get_chunks_tool",
                "description": f"Exception occurred: {str(e)}"
            })
            error_msg = f"Error retrieving chunks from Elasticsearch: {str(e)}"
            return error_msg

    @tool
    def get_sql_data_tool(query: str) -> str:
        """
        Executes a SQL query against the Incident Management database and returns results.
        
        Args:
            query: The SQL query string to execute.
            
        Returns:
            Formatted string containing the SQL query results or error message
            
        Example SQL Queries:
            - "SELECT * FROM Incidents WHERE Incident_ID = 'INC000229'"
            - "SELECT * FROM Incidents WHERE Status = 'Open' AND Severity = 'P1'"
            - "SELECT Incident_ID, Service_Name, Status, On_Call_Engineer FROM Incidents WHERE On_Call_Engineer = 'Charles Taylor'"
            - "SELECT * FROM Incidents WHERE Status = 'In Progress'"
        """
        try:
            process_flow.append({
                "step_number": 1,
                "agent": "Manager Agent",
                "action": "Analyzing user question",
                "description": f"Analyzing query: {user_query}"
            })
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Manager Agent",
                "action": "Delegating to Incident_Data_Agent",
                "description": f"Routing query to Incident_Data_Agent"
            })

            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_Data_Agent",
                "action": "Connecting to MCP SQL Sever",
                "description": f"Elastablishing connection"
            })
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_Data_Agent",
                "action": "Invoking get_sql_data_tool",
                "description": "Executing SQL query"
            })
            
            
            conn = pyodbc.connect(DB_CONNECTION_STRING)
            cursor = conn.cursor()
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Track step - Fetching results
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_Data_Agent",
                "action": "Fetching query results",
                "description": f"Retrieved {len(rows)} records from database"
            })
            
            if not rows:
                step_num = len(process_flow) + 1
                process_flow.append({
                    "step_number": step_num,
                    "agent": "Incident_Data_Agent",
                    "action": "Formatting final response",
                    "description": "No records found for the query"
                })
                return "No records found matching the query."
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Track step - Processing and formatting results
            step_num = len(process_flow) + 1
            total_records = len(rows)
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_Data_Agent",
                "action": "Processing and formatting results",
                "description": f"Formatting {total_records} records for display"
            })
            
            formatted_results = "Query Results:\n" + "="*100 + "\n"
            
            # Check if records exceed 20
            if total_records > 20:
                formatted_results += f"\nNOTE: Total records found: {total_records}. Displaying first 20 records only.\n"
                formatted_results += "="*100 + "\n\n"
                rows_to_display = rows[:20]
            else:
                formatted_results += "\n"
                rows_to_display = rows
            
            for idx, row in enumerate(rows_to_display, 1):
                formatted_results += f"Record {idx}:\n"
                for col_name, value in zip(columns, row):
                    formatted_results += f"  {col_name}: {value}\n"
                formatted_results += "-"*100 + "\n\n"
            
            cursor.close()
            conn.close()
            return formatted_results
            
        except Exception as e:
            step_num = len(process_flow) + 1
            process_flow.append({
                "step_number": step_num,
                "agent": "Incident_Data_Agent",
                "action": "Error in get_sql_data_tool",
                "description": f"Exception occurred: {str(e)}"
            })
            error_msg = f"Error executing SQL query: {str(e)}"
            return error_msg

    Incident_Data_agent = Agent(
        role="Incident Data Management Assistant",
        goal="Retrieve real-time incident data from the database to answer questions about specific incidents, their status, severity, assigned engineers, and SLA information. For any query about incident details, write and execute SQL queries against the Incidents table.",
        backstory="""
    You are an Incident Data Management Assistant specializing in database queries.

    Your Primary Responsibility:
    - Answer user questions about specific incidents using the Incidents table
    - Execute SQL queries to retrieve incident information

    Database Table: Incidents
    Columns: Incident_ID, Service_Name, Severity, Status, Issue_Description, Owner_Team, On_Call_Engineer, Escalation_Contact, Start_Time, MTTR_Minutes, SLA_Breached

    Query Rules:
    1. When user asks about specific incidents, their status, owner, engineer, or SLA information, use get_sql_data_tool
    2. Construct SQL queries based on the user question:
    - For specific incident: SELECT * FROM Incidents WHERE Incident_ID = '[ID]'
    - For incidents by status: SELECT * FROM Incidents WHERE Status = '[status]'
    - For incidents by severity: SELECT * FROM Incidents WHERE Severity = '[severity]'
    - For incidents by engineer: SELECT * FROM Incidents WHERE On_Call_Engineer = '[name]'
    - For SLA breached incidents: SELECT * FROM Incidents WHERE SLA_Breached = 1
    3. Always use the exact column names and table name
    4. Use ONLY the data returned from SQL queries to construct your answer
    5. Present data in a clear, formatted manner
    6. Do not guess or assume data

    Query Examples and Expected SQL:

    Example 1: User asks "What is the status of incident INC000229?"
    SQL: SELECT Incident_ID, Status, On_Call_Engineer, Severity FROM Incidents WHERE Incident_ID = 'INC000229'

    Example 2: User asks "Who is handling incident INC000284?"
    SQL: SELECT Incident_ID, On_Call_Engineer, Owner_Team, Status FROM Incidents WHERE Incident_ID = 'INC000284'

    Example 3: User asks "Show all open incidents"
    SQL: SELECT * FROM Incidents WHERE Status = 'Open'

    Example 4: User asks "Which incidents have breached SLA?"
    SQL: SELECT Incident_ID, Service_Name, Severity, Status, MTTR_Minutes FROM Incidents WHERE SLA_Breached = 1

    Example 5: User asks "What are all P1 severity incidents?"
    SQL: SELECT * FROM Incidents WHERE Severity = 'P1'

    Tone:
    - Professional
    - Data-focused
    - Clear and concise
    """,
        tools=[get_sql_data_tool],
        llm=llm,
        verbose=True,
    )


    Incident_SOP_agent = Agent(
        role="Incident Management SOP Assistant",
        goal="Answer questions about incident management procedures, escalation paths, and SLAs by retrieving and analyzing relevant information from incident management SOPs and documentation",
        backstory="""
    You are an Incident Management SOP Assistant.

    You must answer user questions ONLY using information returned from the tool:
        get_chunks_tool

    Execution Rules:

    1. For every user question you MUST call:
        use get_chunks_tool, passing the user question as the argument.

    2. Use ONLY the text returned in the chunks to construct the answer.
    3. DO NOT use any prior knowledge outside the chunks.
    4. If the chunks do not contain relevant information, respond EXACTLY:

    "The SOP does not contain enough information to answer this question."

    5. Provide answers in a clear, structured, operational format.
    6. When procedures exist, respond in step-by-step numbered actions.
    7. When severity/SLA is asked, map to P1–P4 definitions from chunks.
    8. Do not mention internal tool names in the final answer.
    9. Do not guess, assume, or hallucinate details.

    Tone:
    - Professional
    - Concise
    - Action oriented for engineers on call

    Formatting Rules:
    - Do NOT use any special characters in your response
    - Do NOT use markdown formatting (bold, italics, code blocks)
    - Keep formatting very clean and professional
    - Use plain text only with simple line breaks and indentation for structure

    """,
        tools=[get_chunks_tool],
        verbose=True,
        llm=llm
    )

    manager_agent = Agent(
        role="Multi-Agent System Manager",
        goal="Intelligently route user queries to the most appropriate specialized agent: either Incident Data Management Assistant or Incident Management SOP Assistant. Ensure coherent and accurate responses.",
        backstory="""You are the manager of a multi-agent system with two specialized agents:

    1. Incident Data Management Assistant
    - Handles: Real-time incident data queries
    - Use when user asks about:
        * Specific incident details (status, severity, owner, engineer)
        * Who is handling a particular incident
        * Incident SLA information
        * Current incident status or metrics
        * Queries about incident IDs, service names, or specific incident attributes
    - Example queries: "What is the status of INC000229?", "Who is handling the authentication incident?", "Show all open incidents"

    2. Incident Management SOP Assistant
    - Handles: Incident management procedures and documentation
    - Use when user asks about:
        * How to handle incidents
        * Escalation procedures
        * SLA definitions and timeframes
        * Incident management best practices
        * Standard Operating Procedures
    - Example queries: "What is the escalation procedure?", "How should we handle P1 incidents?"

    Delegation Logic:
    - If query contains: incident IDs, specific incident names, status questions, engineer assignments, MTTR, or current incident data
    -> Route to: Incident Data Management Assistant
    - If query contains: procedures, how-to, escalation paths, SOP, best practices, definitions
    -> Route to: Incident Management SOP Assistant
    - If query contains BOTH aspects, determine primary intent and route accordingly

    Always ensure the selected agent has all context needed from the user query.""",
        verbose=True,
        llm=llm
    )

    task = Task(
        description=user_query_with_context,
        expected_output="A well-structured, formatted response to the user query"
    )

    # Create and execute the crew
    crew = Crew(
        agents=[Incident_SOP_agent, Incident_Data_agent],
        tasks=[task],
        verbose=True,
        process=Process.hierarchical,
        manager_agent=manager_agent
    )

    crew.kickoff()
    task_output = task.output
    result=task_output.raw
    result=result.replace('*','').replace('#','')
    
    # Return both process_flow list and the result
    return {
        "process_flow": process_flow,
        "response": result
    }

