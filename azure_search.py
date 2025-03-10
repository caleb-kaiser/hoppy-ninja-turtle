from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from typing import Dict, List, Any, Optional
import config


class AzureSearchRetriever:
    """Class for retrieving documents from Azure AI Search."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        index_name: Optional[str] = None,
        top_k: int = config.DEFAULT_TOP_K
    ):
        """Initialize the Azure AI Search retriever."""
        self.endpoint = endpoint or config.AZURE_SEARCH_SERVICE_ENDPOINT
        self.key = key or config.AZURE_SEARCH_ADMIN_KEY
        self.index_name = index_name or config.AZURE_SEARCH_INDEX_NAME
        self.top_k = top_k
        
        if not self.endpoint or not self.key or not self.index_name:
            raise ValueError("Azure Search endpoint, key, and index name must be provided")
        
        # Create a search client
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.key)
        )
    
    def retrieve(self, query: str, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve documents from Azure AI Search.
        
        Args:
            query: The search query
            filter: Optional filter expression
            
        Returns:
            A list of document dictionaries
        """
        # Execute the search
        results = self.search_client.search(
            search_text=query,
            query_type=QueryType.SEMANTIC,
            query_language="en-us",
            semantic_configuration_name="default",
            filter=filter,
            top=self.top_k,
            include_total_count=True
        )
        
        # Convert to list of dictionaries
        docs = []
        for result in results:
            doc = {k: v for k, v in result.items()}
            # Add score if available
            if hasattr(result, "@search.score"):
                doc["score"] = getattr(result, "@search.score")
            # Add reranker score if available
            if hasattr(result, "@search.reranker_score"):
                doc["reranker_score"] = getattr(result, "@search.reranker_score")
            docs.append(doc)
        
        return docs
    
    def retrieve_hybrid(self, query: str, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform a hybrid (keyword + semantic) search.
        
        Args:
            query: The search query
            filter: Optional filter expression
            
        Returns:
            A list of document dictionaries
        """
        # First try semantic search
        try:
            docs = self.retrieve(query, filter)
            if docs:
                return docs
        except Exception as e:
            print(f"Semantic search failed: {e}. Falling back to keyword search.")
        
        # Fall back to keyword search
        results = self.search_client.search(
            search_text=query,
            filter=filter,
            top=self.top_k,
            include_total_count=True
        )
        
        # Convert to list of dictionaries
        docs = []
        for result in results:
            doc = {k: v for k, v in result.items()}
            if hasattr(result, "@search.score"):
                doc["score"] = getattr(result, "@search.score")
            docs.append(doc)
        
        return docs 