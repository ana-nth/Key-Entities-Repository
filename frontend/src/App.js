import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./components/Landing";
import TryOnApp from "./components/TryOnApp";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/tryon" element={<TryOnApp />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;