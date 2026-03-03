import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Download } from 'lucide-react';
import { Button } from '../components/ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Success = () => {
  const [status, setStatus] = useState('checking');
  const [quizId, setQuizId] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const session = urlParams.get('session_id');
    
    if (session) {
      setSessionId(session);
      checkPaymentStatus(session);
    }
  }, []);

  const checkPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    
    if (attempts >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/checkout/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setStatus('success');
        setQuizId(response.data.metadata.quiz_id);
      } else if (response.data.status === 'expired') {
        setStatus('failed');
      } else {
        setTimeout(() => checkPaymentStatus(sessionId, attempts + 1), 2000);
      }
    } catch (err) {
      console.error('Error checking status:', err);
      setStatus('error');
    }
  };

  const handleDownload = () => {
    window.open(`${API}/pdf/download/${quizId}`, '_blank');
  };

  if (status === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Verifying your payment...</p>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl text-center"
        >
          <div className="mb-6">
            <CheckCircle2 className="w-20 h-20 text-primary mx-auto" strokeWidth={1.5} />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight mb-4">
            Payment Successful
          </h1>
          <p className="text-lg text-muted-foreground mb-10 leading-relaxed">
            Your personalized 365 Days of Discipline blueprint is ready.
          </p>
          
          <Button
            data-testid="download-pdf-btn"
            onClick={handleDownload}
            size="lg"
            className="bg-primary hover:bg-primary/90 text-white text-base px-12 py-6 rounded-full font-semibold glow-purple-hover transition-all duration-300"
          >
            <Download className="w-5 h-5 mr-2" />
            Download Your PDF
          </Button>

          <div className="mt-12 bg-card border border-border/40 rounded-2xl p-8">
            <p className="text-sm text-muted-foreground mb-2 leading-relaxed">Remember:</p>
            <p className="font-semibold leading-relaxed">Consistency beats perfection. Follow this plan for at least 8-12 weeks.</p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold mb-4">Payment {status === 'timeout' ? 'Timeout' : 'Failed'}</h1>
        <p className="text-muted-foreground mb-6">
          {status === 'timeout' 
            ? 'Payment verification timed out. Please check your email or contact support.'
            : 'Payment was not successful. Please try again.'}
        </p>
        <Button
          onClick={() => window.location.href = '/'}
          variant="outline"
        >
          Return Home
        </Button>
      </div>
    </div>
  );
};