import opik


class RetreiverService:
    def __init__(self):
        self.client = opik.Opik()
        self.current_trace = None
    
    # Stub user query for now. Should return list of docs
    def retreive(self, query: str):
        output = {
            "docs": ["doc1", "doc2", "doc3"],
        }

        self.current_trace.span(
            name="retreive",
            input={"query": query},
            output={"output": output},
        )
        return output
    
    # Stub post-process for now. Should return list of docs
    def post_process(self, docs: list):
        output = {
            "docs": ["doc1", "doc2", "doc3"],
        }

        self.current_trace.span(
            name="post_process",
            input={"docs": docs},
            output={"output": output},
        )
        return output
    
    # Stub construct_prompt for now. Should return prompt
    def construct_prompt(self, docs: list):
        output = {
            "prompt": "prompt",
        }

        self.current_trace.span(
            name="construct_prompt",
            input={"docs": docs},
            output={"output": output},
        )
        return output
    
    # Stub call_llm for now. Should return response
    def call_llm(self, prompt: str):
        output = {
            "response": "response",
        }

        self.current_trace.span(
            name="call_llm",
            input={"prompt": prompt},
            output={"output": output},
        )
        return output
    
    def eval_response(self, response: str):
        output = {
            "status": "success",
        }
        
        return output
    
    def __call__(self, query: str):
        self.current_trace = self.client.trace(name="test-retriever", input={"initial_query": query})


        docs = self.retreive(query)
        docs = self.post_process(docs)
        prompt = self.construct_prompt(docs)
        response = self.call_llm(prompt)
        return response

# Remove indentation for the main block
if __name__ == "__main__":
    retreiver_service = RetreiverService()
    response = retreiver_service("query")
    print(response)
    



