import React from 'react';
import { useNavigate } from 'react-router-dom';
import { APP_NAME } from '../config/constants';
import logo from '../assets/logo.svg';

const Toolbar = () => {
  const navigate = useNavigate();

  return (
    <div className="toolbar">
      <div className="toolbar-content">
        <img 
          src={logo}
          className="logo"
          onClick={() => navigate('/')}
          width="40" 
          height="40" 
          alt="Company Logo"
          style={{ cursor: 'pointer' }}
        />
        <div className="separator"></div>
        <h1>{APP_NAME}</h1>
      </div>
    </div>
  );
};

export default Toolbar; 