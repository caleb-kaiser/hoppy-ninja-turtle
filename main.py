import opik
import time
import json
from typing import Dict, List, Any, Optional
import config
from azure_search import AzureSearchRetriever
from evaluator import RAGEvaluator
from openai import OpenAI


class RetrieverService:
    def __init__(self):
        # Initialize Opik client for tracing
        self.client = opik.Opik()
        self.current_trace = None
        
        # Initialize Azure AI Search
        self.search_retriever = AzureSearchRetriever(
            endpoint=config.AZURE_SEARCH_SERVICE_ENDPOINT,
            key=config.AZURE_SEARCH_ADMIN_KEY,
            index_name=config.AZURE_SEARCH_INDEX_NAME,
            top_k=config.DEFAULT_TOP_K
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Initialize evaluator
        self.evaluator = RAGEvaluator(opik_client=self.client)
        
        # Store the original docs and processed docs for evaluation
        self.original_docs = []
        self.processed_docs = []
    
    def retrieve(self, query: str):
        """Retrieve documents from Azure AI Search."""
        start_time = time.time()
        
        try:
            # Try hybrid retrieval (semantic + keyword fallback)
            docs = self.search_retriever.retrieve_hybrid(query)
            
            # Format the output
            output = {
                "docs": docs,
                "count": len(docs)
            }
            
            # Store original docs for evaluation
            self.original_docs = docs
            
            # Record the span in Opik
            end_time = time.time()
            self.current_trace.span(
                name="retrieve",
                input={"query": query},
                output={"output": output},
                metadata={"latency_ms": (end_time - start_time) * 1000}
            )
            
            return output
        except Exception as e:
            # Record the error in Opik
            self.current_trace.span(
                name="retrieve",
                input={"query": query},
                metadata={"error": str(e)},
            )
            raise
    
    def post_process(self, docs_container: Dict[str, Any]):
        """Process the retrieved documents."""
        start_time = time.time()
        docs = docs_container.get("docs", [])
        
        try:
            # Example post-processing: sort by score and deduplicate
            if docs:
                # Sort by score if available
                if "score" in docs[0]:
                    docs = sorted(docs, key=lambda x: x.get("score", 0), reverse=True)
                
                # Deduplicate by content (assuming there's a 'content' field)
                seen_content = set()
                deduplicated_docs = []
                
                for doc in docs:
                    # Use a relevant field for deduplication - adjust as needed
                    content_key = doc.get("content", "") or doc.get("text", "") or str(doc)
                    if content_key not in seen_content:
                        seen_content.add(content_key)
                        deduplicated_docs.append(doc)
                
                docs = deduplicated_docs[:config.DEFAULT_TOP_K]  # Limit to top_k
            
            # Store processed docs for evaluation
            self.processed_docs = docs
            
            output = {
                "docs": docs,
                "count": len(docs)
            }
            
            # Record the span in Opik
            end_time = time.time()
            self.current_trace.span(
                name="post_process",
                input={"docs_container": docs_container},
                output={"output": output},
                metadata={"latency_ms": (end_time - start_time) * 1000}
            )
            
            return output
        except Exception as e:
            # Record the error in Opik
            self.current_trace.span(
                name="post_process",
                input={"docs_container": docs_container},
                metadata={"error": str(e)},
            )
            raise
    
    def construct_prompt(self, docs_container: Dict[str, Any]):
        """Construct a prompt using the processed documents."""
        start_time = time.time()
        docs = docs_container.get("docs", [])
        
        try:
            # Create context from document content
            context = ""
            for i, doc in enumerate(docs):
                # Extract the content field (adjust based on your document schema)
                content = doc.get("content", "") or doc.get("text", "") or str(doc)
                source = doc.get("source", "") or doc.get("url", "") or f"Document {i+1}"
                
                # Add to context
                context += f"\n\nDocument {i+1} (Source: {source}):\n{content}"
            
            # Construct the full prompt with system instructions
            prompt = f"""You are a helpful assistant answering questions based on the provided documents.
            
CONTEXT:
{context}

Please answer the question based only on the information provided in the documents above. If you don't know the answer or the information is not in the documents, say so clearly.

Question: {{query}}

Answer:"""
            
            output = {
                "prompt": prompt
            }
            
            # Record the span in Opik
            end_time = time.time()
            self.current_trace.span(
                name="construct_prompt",
                input={"docs_container": docs_container},
                output={"output": output},
                metadata={"latency_ms": (end_time - start_time) * 1000}
            )
            
            return output
        except Exception as e:
            # Record the error in Opik
            self.current_trace.span(
                name="construct_prompt",
                input={"docs_container": docs_container},
                metadata={"error": str(e)}
            )
            raise
    
    def call_llm(self, prompt_container: Dict[str, Any], query: str):
        """Call the LLM with the constructed prompt."""
        start_time = time.time()
        prompt_template = prompt_container.get("prompt", "")
        
        try:
            # Insert the query into the prompt template
            prompt = prompt_template.format(query=query)
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model=config.OPENAI_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.DEFAULT_TEMPERATURE,
                max_tokens=config.DEFAULT_MAX_TOKENS
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            
            output = {
                "response": response_text,
                "model": config.OPENAI_MODEL_NAME,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # Record the span in Opik
            end_time = time.time()
            self.current_trace.span(
                name="call_llm",
                input={"prompt": prompt, "query": query},
                output={"output": output},
                metadata={
                    "latency_ms": (end_time - start_time) * 1000,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
            
            return output
        except Exception as e:
            # Record the error in Opik
            self.current_trace.span(
                name="call_llm",
                input={"prompt_container": prompt_container, "query": query},
                metadata={"error": str(e)}
            )
            raise
    
    def __call__(self, query: str):
        """Execute the full RAG pipeline."""
        # Start the trace
        pipeline_start_time = time.time()
        self.current_trace = self.client.trace(
            name="rag-pipeline", 
            input={"initial_query": query}
        )
        
        try:
            # Execute the RAG pipeline
            docs_container = self.retrieve(query)
            processed_docs_container = self.post_process(docs_container)
            prompt_container = self.construct_prompt(processed_docs_container)
            response_container = self.call_llm(prompt_container, query)
            
            # Calculate total latency
            pipeline_end_time = time.time()
            total_latency_ms = (pipeline_end_time - pipeline_start_time) * 1000
            
            # Prepare the final response
            final_response = {
                "query": query,
                "response": response_container.get("response", ""),
                "model": response_container.get("model", config.OPENAI_MODEL_NAME),
                "latency_ms": total_latency_ms,
                "trace_id": self.current_trace.id
            }
            
            
            return final_response
        except Exception as e:
            
            # Re-raise the exception
            raise


# Entry point
if __name__ == "__main__":
    print("Starting RAG pipeline demo...")
    
    # Create the retriever service
    retriever_service = RetrieverService()
    
    # Example query
    query = "What is the capital of France?"
    print(f"Query: {query}")
    
    # Execute the RAG pipeline
    try:
        response = retriever_service(query)
        print("\nResults:")
        print(f"Response: {response['response']}")
        print(f"Latency: {response['latency_ms']:.2f} ms")
        print(f"Trace ID: {response['trace_id']}")
    except Exception as e:
        print(f"Error executing RAG pipeline: {e}")
    



