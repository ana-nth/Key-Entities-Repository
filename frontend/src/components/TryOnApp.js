import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./TryOnApp.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const TryOnApp = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  
  // Form data
  const [formData, setFormData] = useState({
    userImage: null,
    clothingImage: null,
    measurements: {
      height: "",
      weight: "",
      chest: "",
      waist: "",
      hips: ""
    },
    style: "casual",
    name: ""
  });
  
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleImageUpload = (field, file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData(prev => ({
          ...prev,
          [field]: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const validateForm = () => {
    if (!formData.userImage) {
      setError("Please upload your photo");
      return false;
    }
    if (!formData.clothingImage) {
      setError("Please upload a clothing image");
      return false;
    }
    if (!formData.name.trim()) {
      setError("Please enter your name");
      return false;
    }
    const { height, weight, chest, waist, hips } = formData.measurements;
    if (!height || !weight || !chest || !waist || !hips) {
      setError("Please fill in all measurement fields");
      return false;
    }
    return true;
  };

  const generateTryOn = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    setError("");
    setLoadingMessage("Preparing your virtual try-on...");
    
    try {
      // Create try-on request
      setLoadingMessage("Analyzing your photo and measurements...");
      
      const requestData = {
        name: formData.name,
        user_image: formData.userImage,
        clothing_image: formData.clothingImage,
        measurements: formData.measurements,
        style: formData.style
      };

      const response = await fetch(`${BACKEND_URL}/api/tryon/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      setLoadingMessage("Creating your ultra-realistic 3D model...");
      
      const data = await response.json();
      
      if (data.success) {
        setLoadingMessage("Finalizing your virtual try-on...");
        setResult(data);
        setStep(3); // Move to results step
      } else {
        throw new Error(data.error || "Failed to generate try-on");
      }
      
    } catch (err) {
      console.error("Try-on generation error:", err);
      setError(`Failed to generate virtual try-on: ${err.message}`);
    } finally {
      setLoading(false);
      setLoadingMessage("");
    }
  };

  const resetForm = () => {
    setFormData({
      userImage: null,
      clothingImage: null,
      measurements: {
        height: "",
        weight: "",
        chest: "",
        waist: "",
        hips: ""
      },
      style: "casual",
      name: ""
    });
    setResult(null);
    setError("");
    setStep(1);
  };

  const nextStep = () => {
    if (step === 1 && (!formData.userImage || !formData.clothingImage || !formData.name)) {
      setError("Please complete all fields before proceeding");
      return;
    }
    setError("");
    setStep(step + 1);
  };

  const prevStep = () => {
    setError("");
    setStep(step - 1);
  };

  return (
    <div className="tryon-app">
      {/* Header */}
      <header className="app-header">
        <div className="container">
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
          <h1 className="app-title">Virtual Try-On Studio</h1>
          <div className="step-indicator">
            Step {step} of 3
          </div>
        </div>
      </header>

      <div className="container">
        {loading && (
          <div className="loading-overlay">
            <div className="loading-content">
              <div className="loading-spinner"></div>
              <h3>{loadingMessage}</h3>
              <p>Please wait while we create your virtual try-on...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError("")} className="error-close">×</button>
          </div>
        )}

        {/* Step 1: Image Uploads */}
        {step === 1 && (
          <div className="step-container">
            <h2 className="step-title">Upload Your Images</h2>
            <div className="upload-grid">
              <div className="upload-section">
                <h3>Your Photo</h3>
                <div className="upload-area">
                  {formData.userImage ? (
                    <div className="image-preview">
                      <img src={formData.userImage} alt="Your photo" />
                      <button 
                        className="remove-image"
                        onClick={() => handleInputChange('userImage', null)}
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <label className="upload-label">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleImageUpload('userImage', e.target.files[0])}
                      />
                      <div className="upload-placeholder">
                        <span className="upload-icon">📸</span>
                        <span>Click to upload your photo</span>
                      </div>
                    </label>
                  )}
                </div>
              </div>

              <div className="upload-section">
                <h3>Clothing Item</h3>
                <div className="upload-area">
                  {formData.clothingImage ? (
                    <div className="image-preview">
                      <img src={formData.clothingImage} alt="Clothing item" />
                      <button 
                        className="remove-image"
                        onClick={() => handleInputChange('clothingImage', null)}
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <label className="upload-label">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleImageUpload('clothingImage', e.target.files[0])}
                      />
                      <div className="upload-placeholder">
                        <span className="upload-icon">👕</span>
                        <span>Click to upload clothing</span>
                      </div>
                    </label>
                  )}
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Your Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter your name"
                className="form-input"
              />
            </div>

            <div className="step-actions">
              <button className="primary-button" onClick={nextStep}>
                Next: Add Measurements →
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Measurements */}
        {step === 2 && (
          <div className="step-container">
            <h2 className="step-title">Your Measurements</h2>
            <p className="step-subtitle">Enter your measurements for the most accurate fit</p>
            
            <div className="measurements-grid">
              <div className="form-group">
                <label>Height (cm)</label>
                <input
                  type="number"
                  value={formData.measurements.height}
                  onChange={(e) => handleInputChange('measurements.height', e.target.value)}
                  placeholder="170"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Weight (kg)</label>
                <input
                  type="number"
                  value={formData.measurements.weight}
                  onChange={(e) => handleInputChange('measurements.weight', e.target.value)}
                  placeholder="65"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Chest (cm)</label>
                <input
                  type="number"
                  value={formData.measurements.chest}
                  onChange={(e) => handleInputChange('measurements.chest', e.target.value)}
                  placeholder="90"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Waist (cm)</label>
                <input
                  type="number"
                  value={formData.measurements.waist}
                  onChange={(e) => handleInputChange('measurements.waist', e.target.value)}
                  placeholder="75"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Hips (cm)</label>
                <input
                  type="number"
                  value={formData.measurements.hips}
                  onChange={(e) => handleInputChange('measurements.hips', e.target.value)}
                  placeholder="95"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label>Style Preference</label>
                <select
                  value={formData.style}
                  onChange={(e) => handleInputChange('style', e.target.value)}
                  className="form-input"
                >
                  <option value="casual">Casual</option>
                  <option value="formal">Formal</option>
                  <option value="sporty">Sporty</option>
                  <option value="trendy">Trendy</option>
                </select>
              </div>
            </div>

            <div className="step-actions">
              <button className="secondary-button" onClick={prevStep}>
                ← Back
              </button>
              <button className="primary-button" onClick={generateTryOn}>
                Generate Virtual Try-On ✨
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {step === 3 && result && (
          <div className="step-container">
            <h2 className="step-title">Your Virtual Try-On Result</h2>
            <p className="step-subtitle">Here's how the outfit looks on you!</p>
            
            <div className="result-container">
              <div className="result-image">
                {result.tryon_image && (
                  <img src={result.tryon_image} alt="Virtual try-on result" />
                )}
              </div>
              
              <div className="result-info">
                <h3>Try-On Details</h3>
                <div className="detail-item">
                  <strong>Name:</strong> {formData.name}
                </div>
                <div className="detail-item">
                  <strong>Style:</strong> {formData.style}
                </div>
                <div className="detail-item">
                  <strong>Generated:</strong> {new Date().toLocaleDateString()}
                </div>
                {result.feedback && (
                  <div className="detail-item">
                    <strong>AI Feedback:</strong> {result.feedback}
                  </div>
                )}
              </div>
            </div>

            <div className="step-actions">
              <button className="secondary-button" onClick={resetForm}>
                Try Another Outfit
              </button>
              <button className="primary-button" onClick={() => navigate('/')}>
                Back to Home
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TryOnApp;