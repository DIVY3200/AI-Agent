# AI Agent

An AI agent that reads through a dataset (CSV or Google Sheets) and performs a
web search to retrieve specific information for each entity in a chosen column. The AI will leverage
an LLM to parse web results based on the user's query and format the extracted data in a
structured output. The project includes building a simple dashboard where users can upload a file,
define search queries, and view/download the results.

## Features

#### 1. Data Source Selection
 Users can choose the source of data:
- **Upload CSV**: Users can upload a CSV file for data processing.
- **Google Sheets**: Users can connect to a Google Sheet by providing its URL.

#### 2. Data Preview
- The application displays a preview of the uploaded or connected data for verification before processing.

#### 3. Entity Selection
- Users can select the column in the data that contains the entities for extraction.

#### 4. Prompt Configuration
- Users can provide a customizable prompt template for entity-specific data extraction.
Example: "Get me the email address of {company}"

#### 5. Search and LLM Processing
The application performs two tasks:
- **Upload CSV**: Users can upload a CSV file for data processing.
- **Google Sheets**: Users can connect to a Google Sheet by providing its URL.

#### 6. Tabular Results Display
 The application organizes results into two sections:
- **LLM Processed Results**: Displays extracted information such as:
     - **Extracted Info** (e.g., email, phone, address).
     - **Confidence level** of the result.
     - **Source** of the extracted information.

- **LLM Processing**: Processes the search results using a language model (e.g., OpenAI GPT) to extract relevant information

#### 7. Download Options
 Users can download:
- **Processed Results** (LLM processed data) in CSV format..
- **Raw Search Results** in CSV format.

#### 8. User-Friendly Interface
Built using Streamlit, providing an interactive dashboard with:
- Tabs for better navigation.
- Sidebar options for quick configuration.
- Intuitive file upload and text input fields.

#### 9. Real-Time Feedback
Features real-time status updates:
- Success messages for uploaded files or connected Google Sheets.
- A loading spinner during processing.

#### 10. Environment Configurations
- Environment variables (e.g., API keys) are securely loaded from a .env file, ensuring privacy and security.

#### 11. Extendable for Various Use Cases
 Can be extended for:
- Extracting different types of data (e.g., social media links, contact details).
- Adapting prompts for specific use cases (e.g., job listings, company profiles).

## Requirements
- **Dashboard/UI**: Streamlit, Flask
- **Data Handling**: pandas for CSV files; Google Sheets API for Sheets
- **Search API**: SerpAPI, ScraperAPI, or another search service
- **LLM API**: Groq or OpenAI’s GPT API
- **Backend**: Python
- **Agents**: Langchain

## Installation

1. Install Dependencies: 
```
pip install -r requirements
```

2. Edit .env file with your API keys:
```
GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_key
GOOGLE_SHEETS_CREDENTIALS=path_to_credentials.json
```

## Project Structure Directory
```
ai-agent/
├── app.py                 
├── __pycache__/
|             | - config.cpython-310.pyc 
│   ├── models/ 
│   │   ├── __pycache__
|                        |-llm_processing.cpython-310.pyc 
│   │   ├── llm_processing.py            
│   ├── services/ 
│   │   ├── __pycache__
|                         |-google_sheets.cpython-310.pyc
|                         | - search_api.cpython-310.pyc
│   │   └── google_sheets.py
|           |-search_api.py   
│   ├── utils/ 
│   │   ├── __pycache__
|                        |-file_handler.cpython-310.pyc
│   │   ├── data_processing.py      
│   │   └── file_handler.py   
│  
├── .gitignore                                  
├── app.log
| ---- app.py
| ----  config.py
| ---- llm_processor.log   
└── requirements.txt
```

## Start The Application
```
streamlit run app.py
```

## Multiple Field Extraction
Extract multiple pieces of information in a single query:

```
prompt = """
Extract the following information for {company}:
- Email address
- Physical address
- Phone number
- Founded year

Format the output as JSON.
"""
```

## Links
 - [Streamlit](https://streamlit.io/)
 - [Groq](https://groq.com/)
 - [SerpAPI](https://serpapi.com/)
