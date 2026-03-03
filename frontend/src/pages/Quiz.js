import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const QUESTIONS = [
  {
    id: 'age',
    question: 'How old are you?',
    type: 'number',
    placeholder: 'Enter your age',
    min: 13,
    max: 80,
  },
  {
    id: 'gender',
    question: 'What is your gender?',
    type: 'choice',
    options: [
      { value: 'male', label: 'Male' },
      { value: 'female', label: 'Female' },
    ],
  },
  {
    id: 'height',
    question: 'What is your height?',
    type: 'number',
    placeholder: 'Height in cm',
    min: 120,
    max: 250,
    suffix: 'cm',
  },
  {
    id: 'weight',
    question: 'What is your current weight?',
    type: 'number',
    placeholder: 'Weight in kg',
    min: 30,
    max: 200,
    suffix: 'kg',
  },
  {
    id: 'experience_level',
    question: 'What is your training experience?',
    type: 'choice',
    options: [
      { value: 'beginner', label: 'Beginner', subtitle: '0-6 months' },
      { value: 'intermediate', label: 'Intermediate', subtitle: '6-24 months' },
      { value: 'advanced', label: 'Advanced', subtitle: '2+ years' },
    ],
  },
  {
    id: 'goal',
    question: 'What is your primary goal?',
    type: 'choice',
    options: [
      { value: 'gain_muscle', label: 'Gain Muscle' },
      { value: 'lose_fat', label: 'Lose Fat' },
      { value: 'recomposition', label: 'Recomposition', subtitle: 'Gain muscle + lose fat' },
    ],
  },
  {
    id: 'training_days',
    question: 'How many days per week can you train?',
    type: 'choice',
    options: [
      { value: 3, label: '3 Days' },
      { value: 4, label: '4 Days' },
      { value: 5, label: '5 Days' },
      { value: 6, label: '6 Days' },
    ],
  },
  {
    id: 'equipment',
    question: 'What equipment do you have access to?',
    type: 'choice',
    options: [
      { value: 'full_gym', label: 'Full Gym' },
      { value: 'dumbbells', label: 'Dumbbells Only' },
      { value: 'bodyweight', label: 'Bodyweight Only' },
    ],
  },
  {
    id: 'dietary_preference',
    question: 'What is your dietary preference?',
    type: 'choice',
    options: [
      { value: 'non_vegetarian', label: 'Non-Vegetarian' },
      { value: 'eggitarian', label: 'Eggitarian' },
      { value: 'vegetarian', label: 'Vegetarian' },
    ],
  },
  {
    id: 'sleep_hours',
    question: 'How many hours do you sleep on average?',
    type: 'choice',
    options: [
      { value: 'less_5', label: 'Less than 5 hours' },
      { value: '5_6', label: '5-6 hours' },
      { value: '6_7', label: '6-7 hours' },
      { value: '7_plus', label: '7+ hours' },
    ],
  },
  {
    id: 'injuries',
    question: 'Do you have any injuries or limitations?',
    type: 'text',
    placeholder: 'Optional - Leave blank if none',
    optional: true,
  },
];

export const Quiz = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const currentQuestion = QUESTIONS[currentStep];
  const progress = ((currentStep + 1) / QUESTIONS.length) * 100;

  const handleChoice = (value) => {
    setAnswers({ ...answers, [currentQuestion.id]: value });
    setTimeout(() => {
      if (currentStep < QUESTIONS.length - 1) {
        setCurrentStep(currentStep + 1);
        setInputValue('');
      } else {
        submitQuiz({ ...answers, [currentQuestion.id]: value });
      }
    }, 200);
  };

  const handleNumberInput = () => {
    const num = parseFloat(inputValue);
    if (isNaN(num) || num < currentQuestion.min || num > currentQuestion.max) {
      setError(`Please enter a value between ${currentQuestion.min} and ${currentQuestion.max}`);
      return;
    }
    setError('');
    handleChoice(num);
  };

  const handleTextInput = () => {
    handleChoice(inputValue || '');
  };

  const submitQuiz = async (finalAnswers) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/quiz/submit`, finalAnswers);
      onComplete(response.data, finalAnswers);
    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError('Failed to submit. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <Progress value={progress} className="h-1 rounded-none" />
      </div>

      <div className="flex-1 flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-2xl">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              data-testid={`quiz-step-${currentStep}`}
            >
              <p className="text-xs uppercase tracking-widest font-semibold text-accent mb-4">
                QUESTION {currentStep + 1} OF {QUESTIONS.length}
              </p>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight leading-tight mb-10">
                {currentQuestion.question}
              </h2>

              {currentQuestion.type === 'choice' && (
                <div className="space-y-4">
                  {currentQuestion.options.map((option) => (
                    <motion.button
                      key={option.value}
                      data-testid={`option-${option.value}`}
                      onClick={() => handleChoice(option.value)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full bg-card border-2 border-border/40 hover:border-primary transition-all duration-300 rounded-2xl p-6 text-left glow-purple-hover"
                    >
                      <div className="font-bold text-lg">{option.label}</div>
                      {option.subtitle && (
                        <div className="text-sm text-muted-foreground mt-1">{option.subtitle}</div>
                      )}
                    </motion.button>
                  ))}
                </div>
              )}

              {(currentQuestion.type === 'number' || currentQuestion.type === 'text') && (
                <div>
                  <div className="flex gap-4">
                    <input
                      data-testid={`input-${currentQuestion.id}`}
                      type={currentQuestion.type === 'number' ? 'number' : 'text'}
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          currentQuestion.type === 'number' ? handleNumberInput() : handleTextInput();
                        }
                      }}
                      placeholder={currentQuestion.placeholder}
                      className="flex-1 bg-secondary border-2 border-transparent focus:border-primary focus:ring-2 focus:ring-primary/30 h-14 text-lg px-4 rounded-2xl transition-all"
                      min={currentQuestion.min}
                      max={currentQuestion.max}
                    />
                    <Button
                      data-testid="submit-answer-btn"
                      onClick={currentQuestion.type === 'number' ? handleNumberInput : handleTextInput}
                      disabled={!currentQuestion.optional && !inputValue}
                      size="lg"
                      className="bg-primary hover:bg-primary/90 h-14 px-6 rounded-2xl glow-purple-hover"
                    >
                      <ChevronRight className="w-6 h-6" />
                    </Button>
                  </div>
                  {currentQuestion.suffix && (
                    <p className="text-sm text-muted-foreground mt-2">In {currentQuestion.suffix}</p>
                  )}
                  {error && <p className="text-accent text-sm mt-2">{error}</p>}
                </div>
              )}

              {loading && (
                <div className="text-center mt-8">
                  <p className="text-muted-foreground">Calculating your protocol...</p>
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};