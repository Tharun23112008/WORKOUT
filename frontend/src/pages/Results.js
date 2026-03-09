import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle2, X, QrCode, Upload } from 'lucide-react';
import { Button } from '../components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Results = ({ results, quizId }) => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentScreenshot, setPaymentScreenshot] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending');

  useEffect(() => {
    if (showPaymentModal) {
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.width = '100%';
      document.documentElement.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.documentElement.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.width = '';
      document.documentElement.style.overflow = '';
    };
  }, [showPaymentModal]);

  const handleUnlock = () => setShowPaymentModal(true);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) setPaymentScreenshot(file);
  };

  const handleSubmitPayment = async () => {
    if (!paymentScreenshot) {
      alert('Please upload payment screenshot');
      return;
    }
    setPaymentStatus('uploading');
    setTimeout(() => {
      setPaymentStatus('success');
      alert('Payment confirmation submitted! You will receive your PDF via email within 24 hours after verification.');
    }, 2000);
  };

  return (
    <div className="min-h-screen py-10 sm:py-20 px-4 sm:px-6 relative">
      {/* Gradient Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-primary rounded-full blur-[150px] opacity-20"></div>
        <div className="absolute bottom-1/4 left-0 w-64 sm:w-96 h-64 sm:h-96 bg-secondary rounded-full blur-[150px] opacity-20"></div>
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight mb-3 text-center">
            <span className="gradient-text">Your Free Snapshot</span>
          </h1>
          <p className="text-center text-muted-foreground mb-10 sm:mb-16 leading-relaxed text-base sm:text-lg">
            This is 15% of your personalized plan
          </p>

          {/* Free Preview Section */}
          <div className="glass-morphism-strong rounded-2xl sm:rounded-3xl p-6 sm:p-12 mb-8 sm:mb-12 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 sm:w-64 h-48 sm:h-64 bg-primary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-48 sm:w-64 h-48 sm:h-64 bg-secondary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>
