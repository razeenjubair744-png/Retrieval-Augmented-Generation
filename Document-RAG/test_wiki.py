import os
os.environ["USER_AGENT"] = "DocumentRAG/1.0 (test@example.com)"

import wikipedia
import traceback

print("Testing Wikipedia API directly with USER_AGENT...")
try:
    res = wikipedia.search("Python programming language")
    print("Search results:", res)
    page = wikipedia.page(res[0])
    print("Page summary:", page.summary[:100])
except Exception as e:
    print("Exception!")
    traceback.print_exc()
