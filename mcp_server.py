from pydantic import Field
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.fastmcp.prompts import base
import asyncio

mcp = FastMCP("DocumentMCP", log_level="WARNING")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

#tool to list all docs
@mcp.tool(
    name="list_all_docs",
    description="List all available documents."
)
def list_documents():
    return list(docs.keys())

#tool to read a doc
@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
async def read_document(
    ctx: Context,
    doc_id: str = Field(description="Id of the document to read")
):
    await ctx.info(f"Cooking call_tool")
    await ctx.report_progress(40,100)
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    await ctx.report_progress(60,100)
    await asyncio.sleep(2)
    await ctx.report_progress(100,100)
    return docs[doc_id]

#tool to edit a doc
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace."),
    new_str: str = Field(description="The new text to insert in place of the old text.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

#resource to return all doc id's
@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())

# resource to return the contents of a particular doc
@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
async def fetch_doc(ctx: Context, doc_id: str) -> str:
    await ctx.info(f"Cooking resource")
    await ctx.report_progress(40,100)
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    await ctx.report_progress(60,100)
    await ctx.report_progress(100,100)
    return docs[doc_id]

#prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrites the contents of the document in Markdown format."
)
def format_document(
    doc_id: str = Field(description="Id of the document to format")
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document to be written with markdown syntax.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Add in headers, bullet points, tables, etc as necessary. Feel free to add in structure.
Use the 'edit_document' tool to edit the document. After the document has been reformatted...
"""
    
    return [
        base.UserMessage(prompt)
    ]

# TODO: Write a prompt to summarize a doc



if __name__ == "__main__":
    mcp.run(transport="stdio")
