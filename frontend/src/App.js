import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import '@/App.css';
import { Landing } from './pages/Landing';
import { Quiz } from './pages/Quiz';
import { Results } from './pages/Results';
import { Success } from './pages/Success';
import { Toaster } from './components/ui/sonner';

function App() {
  const [showQuiz, setShowQuiz] = useState(false);
  const [results, setResults] = useState(null);
  const [quizId, setQuizId] = useState(null);

  const handleStartQuiz = () => {
    setShowQuiz(true);
  };

  const handleQuizComplete = (calculationResults, answers) => {
    setResults(calculationResults);
    setQuizId(calculationResults.quiz_id);
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={
              showQuiz && !results ? (
                <Quiz onComplete={handleQuizComplete} />
              ) : results ? (
                <Results results={results} quizId={quizId} />
              ) : (
                <Landing onStart={handleStartQuiz} />
              )
            } 
          />
          <Route path="/success" element={<Success />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;