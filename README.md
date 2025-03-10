# Hoppy Ninja Turtle

A demo project that shows how to build a RAG (Retrieval-Augmented Generation) pipeline with Azure AI Search and track it with Opik from Comet ML.

## Architecture

The application follows a simple architecture for a RAG pipeline:

1. **Retrieval**: Uses Azure AI Search to retrieve relevant documents based on the user query
2. **Processing**: Post-processes retrieved documents (sorting, deduplication)
3. **Context Construction**: Builds a prompt with the retrieved documents as context
4. **LLM Generation**: Calls OpenAI to generate a response based on the context and query
5. **Evaluation**: Evaluates the quality of the response with various metrics
6. **Tracing**: Uses Opik to track the entire pipeline for observability

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy the `.env` file to your own `.env` file and fill in your credentials:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your own:
   - Azure AI Search credentials
   - OpenAI API key
   - Comet ML/Opik API key

## Project Structure

- `main.py` - Main application with the RAG pipeline implementation
- `azure_search.py` - Helper module for Azure AI Search integration
- `evaluator.py` - RAG evaluation metrics implementation
- `config.py` - Configuration loading from environment variables
- `requirements.txt` - Dependencies

## Usage

Run the application with:

```
python main.py
```

This will run a simple example query through the RAG pipeline.

## Customization

### Using Your Own Azure AI Search Index

To use your own Azure AI Search index:

1. Create an index in the Azure portal with your documents
2. Update the `.env` file with your index details
3. Adjust the document field names in the code if necessary (in `construct_prompt` method)

### Tracking with Opik

The application uses Opik to create traces for each query and spans for each step in the pipeline. This allows you to:

1. Track latency of each component
2. Observe inputs and outputs at each step
3. Monitor token usage and costs
4. Analyze evaluation metrics over time

View your traces in the Comet ML dashboard.

## Evaluation Metrics

The evaluation layer includes several metrics:

1. **Relevance**: How relevant the retrieved documents are to the query
2. **Faithfulness**: Whether the response is faithful to the retrieved content
3. **Answer Quality**: Overall quality of the generated response
4. **Latency**: End-to-end performance of the pipeline

## Future Improvements

1. Add more robust error handling
2. Implement more sophisticated prompt construction
3. Add more advanced evaluation metrics
4. Create a simple web interface
5. Add document ingestion pipeline
