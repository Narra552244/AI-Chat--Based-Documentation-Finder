# AI Chat-Based Documentation Finder

A Streamlit-based application that allows users to query organizational documentation using OpenAI's GPT API. The application provides an intuitive chat interface and supports document upload functionality for administrators.

## Features

- 💬 Chat-based interface for querying documentation
- 📄 Support for PDF and text file uploads
- 🔍 Intelligent search using OpenAI's GPT API
- 📊 Query analytics for administrators
- 🗄️ Document indexing for faster retrieval
- 📝 Query logging for audit purposes

## Architecture

The application is built using the following components:

- **Frontend**: Streamlit
- **LLM Integration**: OpenAI GPT API
- **Document Processing**: PyPDF2, langchain
- **Vector Storage**: FAISS
- **Data Management**: Local file system & SQLite

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── utils/
│   ├── document_processor.py  # Document processing utilities
│   ├── llm_handler.py        # LLM integration
│   ├── db_handler.py         # Database operations
│   └── vector_store.py       # Vector storage management
├── data/
│   ├── documents/           # Uploaded documents
│   └── index/              # Vector index storage
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Usage

1. **Document Upload**:
   - Click on the "Upload Document" button
   - Select PDF or text files to upload
   - The system will process and index the documents automatically

2. **Querying Documents**:
   - Type your question in the chat input
   - The system will search through the indexed documents and provide relevant answers
   - Responses include source references

3. **Admin Features**:
   - Access query analytics
   - View upload history
   - Monitor system performance

## API Guidelines

The application uses OpenAI's GPT API for processing queries. Ensure you have:

1. A valid OpenAI API key
2. Sufficient API credits
3. Proper error handling for API limits

## Security Considerations

- API keys are stored in environment variables
- Document access is controlled
- Query logs are maintained for audit purposes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 