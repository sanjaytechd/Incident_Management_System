# Incident Management AI Assistant

An intelligent multi-agent AI chatbot system for managing and resolving incidents. This application uses CrewAI's hierarchical agent framework to intelligently route incident-related queries to specialized agents that retrieve real-time incident data and management procedures.

## 🌟 Features

### Multi-Agent Intelligence
- **Manager Agent**: Intelligently routes queries to the most appropriate specialized agent
- **Incident Data Management Agent**: Retrieves real-time incident information from SQL Server database
- **Incident Management SOP Agent**: Provides incident management procedures and documentation from Elasticsearch

### Real-Time Incident Management
- Query specific incidents by ID, status, severity, or assigned engineer
- Retrieve incident status, severity, SLA information, and MTTR metrics
- Access incident ownership and escalation contacts

### Knowledge Base Integration
- Semantic search across incident management SOPs and procedures
- Elasticsearch integration for fast, relevant documentation retrieval
- Sentence-Transformers for intelligent query understanding

### Chat History & Persistence
- Persistent chat history stored in SQL Server
- Context-aware responses using previous conversation history
- View, manage, and delete conversation threads

### Web Interface
- Clean, user-friendly Flask web application
- Real-time chat interface with process flow visualization
- Conversation management (view, delete, clear all)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQL Server with IncidentChatHistory table
- Elasticsearch 9.2+ with incident_sop index
- Azure OpenAI API credentials
- ODBC Driver 17 for SQL Server

### Installation

1. **Clone or setup the project directory**
```bash
cd Incident_Chatbot
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**

Update the configuration in `Crewai_agents.py`:
- **Elasticsearch**: Update `ELASTIC_HOST`, `ELASTIC_PORT`, `ELASTIC_USERNAME`, `ELASTIC_PASSWORD`, `ELASTIC_CA_CERT`
- **SQL Server**: Update `DB_CONNECTION_STRING` with your server details
- **Azure OpenAI**: Update the LLM configuration with your Azure endpoint and API key

5. **Setup Database Table**

Create the `IncidentChatHistory` table in your SQL Server database:
```sql
CREATE TABLE IncidentChatHistory (
    ChatID NVARCHAR(MAX),
    Question NVARCHAR(MAX),
    response NVARCHAR(MAX),
    DateTime DATETIME
);
```

### Running the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

- **Home Page**: `http://localhost:5000/`
- **Chat Application**: `http://localhost:5000/app`

## 📋 API Endpoints

### Chat Operations
- **POST** `/query` - Send a query and get AI response
  - Body: `{ "query": "your question", "chatId": "unique-id" }`

- **GET** `/get-conversations` - Fetch all conversations

- **GET** `/get-chat/<chat_id>` - Get specific chat history

- **DELETE** `/delete-chat/<chat_id>` - Delete a specific chat

- **DELETE** `/clear-all` - Clear all conversations

### Pages
- **GET** `/` - Home page
- **GET** `/app` - Chat application interface

## 🏗️ Project Structure

```
Incident_Chatbot/
├── app.py                    # Flask application and API endpoints
├── Crewai_agents.py         # Multi-agent system implementation
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── templates/
    ├── home.html           # Home page template
    └── index.html          # Chat interface template
```

## 🔧 Configuration Details

### Database Connection
Update `DB_CONNECTION_STRING` in both `app.py` and `Crewai_agents.py`:
```python
DB_CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=YOUR_SERVER;Database=YOUR_DB;Trusted_Connection=yes;'
```

### Elasticsearch Configuration
Update in `Crewai_agents.py`:
- `ELASTIC_HOST` - Elasticsearch server hostname
- `ELASTIC_PORT` - Elasticsearch port (default: 9200)
- `ELASTIC_USERNAME` - Elasticsearch username
- `ELASTIC_PASSWORD` - Elasticsearch password
- `ELASTIC_CA_CERT` - Path to CA certificate
- `ELASTIC_INDEX` - Index name (default: incident_sop)

### Azure OpenAI Configuration
Update in `Crewai_agents.py`:
- `api_key` - Your Azure OpenAI API key
- `base_url` - Your Azure OpenAI endpoint
- `api_version` - API version

## 💡 Usage Examples

### Query Incident Status
```
"What is the status of incident INC000229?"
```
The system will route to Incident Data Management Agent and fetch real-time data from SQL Server.

### Get Escalation Procedures
```
"What is the escalation procedure for P1 incidents?"
```
The system will route to Incident Management SOP Agent and retrieve from documentation.

### Find Open Incidents
```
"Show all open incidents"
```
Queries the database for all incidents with Open status.

### Get SOP Information
```
"How should we handle incidents with breached SLA?"
```
Retrieves relevant procedures from the knowledge base.

## 📦 Dependencies

Key Python packages:
- **Flask** - Web framework
- **CrewAI** - Multi-agent orchestration
- **Elasticsearch** - Document search and retrieval
- **sentence-transformers** - Semantic embeddings
- **pyodbc** - SQL Server connectivity
- **Azure OpenAI** - LLM integration

See `requirements.txt` for complete list with versions.

## 🔐 Security Notes

- Store sensitive credentials (API keys, database passwords) in environment variables or secure configuration files
- Never commit credentials to version control
- Use HTTPS in production
- Implement proper authentication for the web interface
- Validate and sanitize all user inputs

## 🐛 Troubleshooting

### Elasticsearch Connection Error
- Verify Elasticsearch is running on the specified host and port
- Check CA certificate path is correct
- Verify credentials are correct

### SQL Server Connection Error
- Check SQL Server is running and accessible
- Verify connection string with correct server name and database
- Ensure ODBC Driver 17 is installed

### Azure OpenAI Errors
- Verify API key and endpoint URL are correct
- Check API version is supported
- Ensure Azure OpenAI resource is active

### Missing Process Flow
- Ensure both agents are properly initialized
- Check LLM configuration is correct
- Verify internet connection for API calls

## 📝 License

This project is proprietary. All rights reserved.

## 👥 Support

For issues or questions, contact the development team.
