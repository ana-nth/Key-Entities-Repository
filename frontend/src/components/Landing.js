import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Landing.css";

const Landing = () => {
  const navigate = useNavigate();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const heroImages = [
    "https://images.unsplash.com/photo-1578632292335-df3abbb0d586",
    "https://images.unsplash.com/photo-1562572159-4efc207f5aff",
    "https://images.pexels.com/photos/3861969/pexels-photo-3861969.jpeg"
  ];

  const clothingImages = [
    "https://images.unsplash.com/photo-1566057155168-bbb743eae26c",
    "https://images.unsplash.com/photo-1561365452-adb940139ffa",
    "https://images.unsplash.com/photo-1551488831-3ed9278737db",
    "https://images.unsplash.com/photo-1611099655360-82662f0b59a8",
    "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb",
    "https://images.unsplash.com/photo-1750000051292-9e951fff46a0"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % heroImages.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [heroImages.length]);

  const features = [
    {
      title: "AI-Powered Virtual Try-On",
      description: "Upload your photo and instantly see how any outfit looks on you with ultra-realistic 3D generation.",
      icon: "🤖"
    },
    {
      title: "Custom Measurements",
      description: "Input your precise measurements for the most accurate fit visualization.",
      icon: "📏"
    },
    {
      title: "Extensive Clothing Library",
      description: "Try on thousands of clothing items from various brands and styles.",
      icon: "👗"
    },
    {
      title: "Instant Results",
      description: "Get your virtual try-on results in seconds with our advanced AI technology.",
      icon: "⚡"
    }
  ];

  return (
    <div className="landing">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              Virtual Try-On
              <span className="gradient-text"> Revolution</span>
            </h1>
            <p className="hero-subtitle">
              Experience the future of fashion with ultra-realistic virtual try-ons. 
              Upload your photo, add your measurements, and see how any outfit looks on you instantly.
            </p>
            <button 
              className="cta-button"
              onClick={() => navigate('/tryon')}
            >
              Start Virtual Try-On
              <span className="button-icon">→</span>
            </button>
          </div>
          <div className="hero-image-container">
            <div className="image-carousel">
              {heroImages.map((img, index) => (
                <img
                  key={index}
                  src={img}
                  alt={`Virtual try-on example ${index + 1}`}
                  className={`hero-image ${index === currentImageIndex ? 'active' : ''}`}
                />
              ))}
            </div>
            <div className="carousel-indicators">
              {heroImages.map((_, index) => (
                <button
                  key={index}
                  className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                  onClick={() => setCurrentImageIndex(index)}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2 className="section-title">Why Choose Our Virtual Try-On?</h2>
          <div className="features-grid">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Clothing Gallery Section */}
      <section className="clothing-gallery">
        <div className="container">
          <h2 className="section-title">Endless Fashion Possibilities</h2>
          <p className="section-subtitle">Try on clothing from top brands and discover your perfect style</p>
          <div className="clothing-grid">
            {clothingImages.map((img, index) => (
              <div key={index} className="clothing-item">
                <img src={img} alt={`Fashion item ${index + 1}`} />
                <div className="clothing-overlay">
                  <span>Try This On</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="final-cta">
        <div className="container">
          <h2 className="cta-title">Ready to Transform Your Shopping Experience?</h2>
          <p className="cta-description">
            Join thousands of users who've revolutionized their fashion choices with our AI-powered virtual try-on technology.
          </p>
          <button 
            className="cta-button large"
            onClick={() => navigate('/tryon')}
          >
            Try It Now - It's Free
            <span className="button-icon">✨</span>
          </button>
        </div>
      </section>
    </div>
  );
};

export default Landing;