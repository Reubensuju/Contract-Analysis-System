import aiosqlite
import os
import json
from datetime import datetime
import io
from PyPDF2 import PdfReader
from typing import List
from .utils.logger import setup_logger

DATABASE_URL = "contracts.db"

# Create logger for this file
logger = setup_logger('database')

async def init_db():
    """Initialize the database and create tables if they don't exist"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                file_data BLOB NOT NULL,
                file_size INTEGER NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status INTEGER DEFAULT 0,
                file_text TEXT,                  -- Stores extracted text content
                parties_involved TEXT,           -- Stored as JSON array
                effective_dates TEXT,            -- Stored as JSON array
                renewal_terms TEXT,              -- Stored as JSON array
                compliance_requirements TEXT,     -- Stored as JSON array
                compliance BOOLEAN DEFAULT FALSE,
                risk TEXT CHECK(risk IN ('low', 'medium', 'high', 'critical', NULL)),
                renewal TEXT CHECK(renewal IN ('pending', 'approved', 'rejected', 'expired', NULL)),
                contract_summary TEXT,           -- Stores contract summary
                potential_risks TEXT             -- Stores risk assessment text
            )
        """)
        await db.commit()

async def insert_document(filename: str, content_type: str, file_data: bytes) -> int:
    """Insert a document into the database and return its ID"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            INSERT INTO documents (
                filename, 
                content_type, 
                file_data, 
                file_size, 
                upload_date
            )
            VALUES (?, ?, ?, ?, ?)
        """, (filename, content_type, file_data, len(file_data), datetime.utcnow()))
        await db.commit()
        return cursor.lastrowid

async def extract_file_text(doc_id: int) -> bool:
    """Extract text from PDF and update the file_text field"""
    try:
        logger.info(f"Starting text extraction for document {doc_id}")
        # First, get the PDF data from the database
        async with aiosqlite.connect(DATABASE_URL) as db:
            cursor = await db.execute("""
                SELECT file_data FROM documents WHERE id = ?
            """, (doc_id,))
            result = await cursor.fetchone()
            
            if not result:
                print(f"Document {doc_id} not found")
                return False
            
            pdf_data = result[0]
            
            # Create a PDF reader object from the binary data
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
            
            # Join all pages with newlines
            full_text = "\n".join(text_content)
            
            # Update the database with extracted text and status
            await db.execute("""
                UPDATE documents 
                SET file_text = ?, status = 1
                WHERE id = ?
            """, (full_text, doc_id))
            await db.commit()
            
            logger.info(f"Completed text extraction for document {doc_id}")
            return True
            
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        return False

async def get_document(doc_id: int):
    """Retrieve a document from the database"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT * FROM documents WHERE id = ?
        """, (doc_id,))
        return await cursor.fetchone()

async def update_document_analysis(
    doc_id: int,
    parties: List[str],
    dates: List[str],
    terms: List[str],
    requirements: List[str],
    compliance: bool,
    risk: str,
    renewal: str,
    contract_summary: str,
    potential_risks: str
) -> bool:
    """Update document analysis results in the database"""
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute("""
                UPDATE documents 
                SET parties_involved = ?,
                    effective_dates = ?,
                    renewal_terms = ?,
                    compliance_requirements = ?,
                    compliance = ?,
                    risk = ?,
                    renewal = ?,
                    contract_summary = ?,
                    potential_risks = ?,
                    status = 5
                WHERE id = ?
            """, (
                json.dumps(parties),
                json.dumps(dates),
                json.dumps(terms),
                json.dumps(requirements),
                compliance,
                risk,
                renewal,
                contract_summary,
                potential_risks,
                doc_id
            ))
            await db.commit()
            return True
    except Exception as e:
        print(f"Error updating document analysis: {str(e)}")
        return False

async def update_document_status(doc_id: int, status: int) -> bool:
    """Update the document status in the database"""
    try:
        async with aiosqlite.connect(DATABASE_URL) as db:
            await db.execute("""
                UPDATE documents 
                SET status = ?
                WHERE id = ?
            """, (status, doc_id))
            await db.commit()
            logger.info(f"Updated status to {status} for document {doc_id}")
            return True
    except Exception as e:
        logger.error(f"Error updating document status: {str(e)}", exc_info=True)
        return False 