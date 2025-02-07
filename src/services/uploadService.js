const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/upload-pdf', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message);
  }
};

export { uploadPDF }; 