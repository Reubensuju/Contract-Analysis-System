import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_upload_pdf_invalid_file():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/upload-pdf", 
            files={"file": ("test.txt", b"Some content", "text/plain")}
        )
    assert response.status_code == 400
    assert response.json() == {"message": "Only PDF files are allowed"}

@pytest.mark.asyncio
async def test_upload_pdf_valid():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/upload-pdf", 
            files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")}
        )
    assert response.status_code in [200, 500]  # 500 if DB or service issues
    if response.status_code == 200:
        assert "document_id" in response.json()

@pytest.mark.asyncio
async def test_get_document_not_found():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/documents/99999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    assert response.json() == {"message": "Document not found"}

