export const fetchDocumentData = async (documentId) => {
  try {
    const response = await fetch(`http://localhost:8000/api/documents/${documentId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch document data');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching document:', error);
    throw error;
  }
}; 