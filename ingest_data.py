import os
import openai

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain.chains import create_qa_chain
from langchain.llms import AzureOpenAI

print("Loading data...")
loader = UnstructuredFileLoader("state_of_the_union.txt")
raw_documents = loader.load()

print("Splitting text...")
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
)
documents = text_splitter.split_documents(raw_documents)

print("Creating vectorstore...")
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["OPENAI_API_KEY"],
    api_version=os.environ["OPENAI_API_VERSION"],
    model="text-embedding-3-large-1"

)

docsearch = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
)

try:
    # Create retrieval chain using create_retrieval_chain
    llm = AzureOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["OPENAI_API_VERSION"],
        model="gpt-4-turbo-0125-preview"
    )

    qa_chain = create_qa_chain(llm, retriever=docsearch.as_retriever(search_kwargs={"k": 1}))

    # Example usage
    query = "What is the main topic of the document?"
    result = qa_chain({"question": query, "chat_history": []})
    print(result)

except openai.OpenAIError as e:
    print(f"Error: {e}")

except Exception as ex:
    print(f"An error occurred: {ex}")

