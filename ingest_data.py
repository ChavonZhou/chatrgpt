import os

from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.chat_loaders.slack import SlackChatLoader
from langchain_community.vectorstores import Chroma
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain.docstore.document import Document

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

print("Loading data...")
loader = SlackChatLoader("chat_history.zip")
raw_sessions = loader.load()

# Convert ChatSessions to Documents
documents = []
for session in raw_sessions:
    for message in session['messages']:
        content = message.content
        sender = message.additional_kwargs.get('sender', 'unknown')
        timestamp = message.additional_kwargs.get('events', [{}])[0].get('message_time', 'unknown')
        documents.append(Document(page_content=content, metadata={"sender": sender, "timestamp": timestamp}))

print("Splitting text...")
text_splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=0,
)
documents = text_splitter.split_documents(documents)

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

print (docsearch)

# try:
#     # Create retrieval chain using create_retrieval_chain
#     llm = AzureOpenAI(
#         api_key=os.environ["OPENAI_API_KEY"],
#         azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
#         api_version=os.environ["OPENAI_API_VERSION"],
#         model="gpt-4-turbo-0125-preview"
#     )
#
#     qa_chain = create_qa_chain(llm, retriever=docsearch.as_retriever(search_kwargs={"k": 1}))
#
#     # Example usage
#     query = "What is the main topic of the document?"
#     result = qa_chain({"question": query, "chat_history": []})
#     print(result)
#
# except openai.OpenAIError as e:
#     print(f"Error: {e}")
#
# except Exception as ex:
#     print(f"An error occurred: {ex}")

