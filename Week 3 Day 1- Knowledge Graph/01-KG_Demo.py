from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. Load the document
loader = TextLoader("sample.txt")
raw_documents = loader.load()

# 2. Initialize the text splitter
# We use a small chunk size here just to see how splitting works
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20
)

# 3. Split the document into chunks
documents = text_splitter.split_documents(raw_documents)

# Let's inspect the chunks
print(f"Total chunks created: {len(documents)}\n")
for i, doc in enumerate(documents):
    print(f"--- Chunk {i+1} ---")
    print(doc.page_content)