import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import Toolbar from './Toolbar';
import { uploadPDF } from '../services/uploadService';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const navigate = useNavigate();

  const onDrop = useCallback(async (acceptedFiles) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile?.type === 'application/pdf') {
      setFile(uploadedFile);
      try {
        const response = await uploadPDF(uploadedFile);
        setUploadStatus({ success: true, filename: response.filename });
        navigate(`/loading/${response.document_id}`, { 
          state: { filename: uploadedFile.name, documentId: response.document_id }
        });
      } catch (error) {
        setUploadStatus({ success: false, error: error.message });
      }
    } else {
      alert('Please upload a PDF file only');
    }
  }, [navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  return (
    <div>
      <Toolbar />
      <div className="app">
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          {file ? (
            <div>
              <p>Selected file: {file.name}</p>
              <button onClick={() => setFile(null)}>Remove file</button>
            </div>
          ) : (
            <div>
              {isDragActive ? (
                <p>Drop the PDF file here</p>
              ) : (
                <p>Drag and drop a PDF file here, or click to select</p>
              )}
            </div>
          )}
        </div>
        {uploadStatus?.error && (
          <div style={{ color: 'red', marginTop: '1rem', textAlign: 'center' }}>
            Upload failed: {uploadStatus.error}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadPage; 