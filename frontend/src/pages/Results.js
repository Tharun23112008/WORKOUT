import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle2, X, QrCode, Upload } from 'lucide-react';
import { Button } from '../components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://workout-cwle.onrender.com';
const API = `${BACKEND_URL}/api`;

export const Results = ({ results, quizId }) => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentScreenshot, setPaymentScreenshot] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending');
  const [userEmail, setUserEmail] = useState('');
  const [emailError, setEmailError] = useState('');

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

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmitPayment = async () => {
    if (!validateEmail(userEmail)) {
      setEmailError('Enter a valid email');
      return;
    }
    if (!paymentScreenshot) {
      alert('Please upload payment screenshot');
      return;
    }

    setPaymentStatus('uploading');

    try {
      const formData = new FormData();
      formData.append('quiz_id', quizId);
      formData.append('email', userEmail);
      formData.append('screenshot', paymentScreenshot);

      const res = await fetch(`${API}/payment/submit`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Server error');
      setPaymentStatus('success');
    } catch (err) {
      alert('Payment submission failed. Please try again.');
      setPaymentStatus('pending');
    }
  };

  return (
    <div className="min-h-screen py-10 sm:py-20 px-4 sm:px-6 relative">
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

            <div className="relative z-10">
              <div className="grid grid-cols-2 gap-4 sm:gap-10">
                <div className="text-center glass-morphism rounded-2xl sm:rounded-3xl p-5 sm:p-10">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-2 sm:mb-3">DAILY CALORIES</p>
                  <p className="text-4xl sm:text-7xl font-black text-white mb-1 sm:mb-2">{results?.calories}</p>
                  <p className="text-xs sm:text-sm text-muted-foreground">kcal per day</p>
                </div>
                <div className="text-center glass-morphism rounded-2xl sm:rounded-3xl p-5 sm:p-10">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-2 sm:mb-3">PROTEIN TARGET</p>
                  <p className="text-4xl sm:text-7xl font-black text-white mb-1 sm:mb-2">{results?.protein}g</p>
                  <p className="text-xs sm:text-sm text-muted-foreground">per day</p>
                </div>
              </div>

              <div className="mt-8 sm:mt-12 pt-8 sm:pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-3 sm:mb-4">YOUR TRAINING STRUCTURE</p>
                <p className="text-base sm:text-xl font-semibold mb-2 sm:mb-3 text-white">{results?.training_plan}</p>
                <p className="text-sm text-muted-foreground leading-relaxed">Based on your experience and weekly availability</p>
              </div>

              <div className="mt-8 sm:mt-12 pt-8 sm:pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-3 sm:mb-4">SAMPLE WORKOUT DAY</p>
                <div className="glass-morphism rounded-xl sm:rounded-2xl p-5 sm:p-8">
                  <p className="font-bold mb-2 text-white text-base sm:text-lg">Monday: Chest</p>
                  <p className="text-sm text-muted-foreground">Bench Press, Incline DB Press, Cable Flyes...</p>
                </div>
              </div>

              <div className="mt-8 sm:mt-12 pt-8 sm:pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-3 sm:mb-4">SAMPLE MEAL IDEA</p>
                <div className="glass-morphism rounded-xl sm:rounded-2xl p-5 sm:p-8">
                  <p className="text-sm text-muted-foreground">
                    Breakfast: Eggs with whole grain toast and avocado (approx. {Math.round((results?.calories || 0) * 0.25)} kcal)
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Paywall Section */}
          <div className="glass-morphism-strong rounded-2xl sm:rounded-3xl p-6 sm:p-14 relative overflow-hidden glow-gradient">
            <div className="absolute top-0 right-0 w-48 sm:w-96 h-48 sm:h-96 bg-primary rounded-full blur-[120px] opacity-20 pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-48 sm:w-96 h-48 sm:h-96 bg-secondary rounded-full blur-[120px] opacity-20 pointer-events-none"></div>

            <div className="relative z-10">
              <div className="flex items-center justify-center gap-4 mb-5 sm:mb-6">
                <div className="bg-gradient-main p-3 sm:p-4 rounded-full glow-gradient">
                  <Lock className="w-7 h-7 sm:w-10 sm:h-10 text-white" />
                </div>
              </div>

              <h2 className="text-2xl sm:text-4xl font-bold tracking-tight mb-3 sm:mb-4 text-center gradient-text">
                Unlock Your Full Protocol
              </h2>
              <p className="text-muted-foreground mb-8 sm:mb-12 leading-relaxed text-base sm:text-lg text-center max-w-2xl mx-auto">
                Get the complete 365 Days of Discipline blueprint
              </p>

              <div className="space-y-3 sm:space-y-4 mb-8 sm:mb-12">
                {[
                  'Complete 7-day training routine with exercise selection',
                  'Detailed sets, reps, rest times, and execution cues',
                  'Full nutrition guide with meal timing and sample plans',
                  'Active rest protocol for faster recovery',
                  'Common mistakes to avoid and discipline reminders',
                  'Exportable high-quality PDF for offline use',
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3 sm:gap-4 glass-morphism rounded-xl sm:rounded-2xl p-4 sm:p-6 hover:glass-morphism-strong transition-all">
                    <div className="bg-gradient-main p-1.5 sm:p-2 rounded-full flex-shrink-0 mt-0.5">
                      <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                    </div>
                    <p className="text-sm sm:text-base leading-relaxed text-white">{item}</p>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <div className="mb-6 sm:mb-8">
                  <span className="text-5xl sm:text-6xl font-black gradient-text">₹499</span>
                  <span className="text-muted-foreground ml-2 sm:ml-3 text-lg sm:text-xl">one-time</span>
                </div>
                <Button
                  onClick={handleUnlock}
                  size="lg"
                  className="bg-gradient-button text-white text-base sm:text-lg px-10 sm:px-16 py-6 sm:py-8 rounded-full font-semibold w-full sm:w-auto glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
                >
                  Pay with FamPay / UPI
                </Button>
                <p className="text-xs text-muted-foreground mt-4 sm:mt-5">Scan QR code to pay securely</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Payment Modal */}
      <AnimatePresence>
        {showPaymentModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-3 sm:p-6"
            onClick={() => setShowPaymentModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-morphism-strong rounded-2xl sm:rounded-3xl p-6 sm:p-10 max-w-lg w-full relative max-h-[92vh] overflow-y-auto"
            >
              {/* X Button */}
              <button
                onClick={() => setShowPaymentModal(false)}
                className="absolute top-4 right-4 sm:top-6 sm:right-6 z-20 glass-morphism p-2 rounded-full hover:glass-morphism-strong transition-all"
              >
                <X className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </button>

              <div className="absolute top-0 right-0 w-48 h-48 bg-primary rounded-full blur-[100px] opacity-20 z-0 pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary rounded-full blur-[100px] opacity-20 z-0 pointer-events-none"></div>

              <div className="relative z-10">
                <div className="text-center mb-6 sm:mb-8">
                  <div className="bg-gradient-main w-14 h-14 sm:w-20 sm:h-20 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 glow-gradient">
                    <QrCode className="w-7 h-7 sm:w-10 sm:h-10 text-white" />
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-bold gradient-text mb-2 sm:mb-3">Scan to Pay ₹499</h2>
                  <p className="text-sm sm:text-base text-muted-foreground">Use any UPI app (FamPay, PhonePe, GPay, Paytm)</p>
                </div>

                {/* QR Code */}
                <div className="flex justify-center mb-6 sm:mb-8">
                  <div className="glass-morphism-strong p-3 sm:p-6 rounded-2xl sm:rounded-3xl glow-gradient">
                    <img
                      src="https://customer-assets.emergentagent.com/job_fitpro-quiz/artifacts/uo7mdy9q_Screenshot_2026-03-03-16-10-35-33_ba41e9a642e6e0e2b03656bfbbffd6e4.jpg"
                      alt="FamPay QR Code"
                      className="w-48 h-48 sm:w-64 sm:h-64 object-contain rounded-xl sm:rounded-2xl"
                    />
                  </div>
                </div>

                {/* UPI ID */}
                <div className="glass-morphism rounded-xl sm:rounded-2xl p-4 sm:p-6 mb-6 sm:mb-8 text-center">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-2">OR USE UPI ID</p>
                  <p className="text-lg sm:text-2xl font-bold text-white">7204042383@fam</p>
                </div>

                {/* Email + Upload */}
                {paymentStatus === 'pending' && (
                  <div className="glass-morphism rounded-2xl p-5 sm:p-8">
                    <p className="text-xs sm:text-sm text-muted-foreground mb-3 font-semibold text-white">Your Email Address <span className="text-primary">*</span></p>
                    <input
                      type="email"
                      placeholder="your@email.com"
                      value={userEmail}
                      onChange={(e) => { setUserEmail(e.target.value); setEmailError(''); }}
                      className="w-full glass-morphism rounded-xl px-4 py-3 text-white text-sm sm:text-base mb-1 outline-none border border-white/10 focus:border-primary/50"
                    />
                    {emailError && <p className="text-red-400 text-xs mb-3">{emailError}</p>}
                    <p className="text-xs text-muted-foreground mb-4 mt-1">We'll send your personalized PDF to this email after payment verification</p>

                    <p className="text-xs sm:text-sm text-muted-foreground mb-3 font-semibold text-white">Upload Payment Screenshot</p>
                    <div className="flex flex-col items-center gap-3 sm:gap-4">
                      <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" id="payment-screenshot" />
                      <label
                        htmlFor="payment-screenshot"
                        className="glass-morphism-strong rounded-full px-6 sm:px-8 py-3 sm:py-4 cursor-pointer hover:glass-morphism transition-all flex items-center gap-3 w-full justify-center"
                      >
                        <Upload className="w-4 h-4 sm:w-5 sm:h-5 text-primary flex-shrink-0" />
                        <span className="text-white text-sm sm:text-base truncate max-w-[200px]">
                          {paymentScreenshot ? paymentScreenshot.name : 'Choose Screenshot'}
                        </span>
                      </label>
                      {paymentScreenshot && (
                        <Button
                          onClick={handleSubmitPayment}
                          className="bg-gradient-button text-white px-8 sm:px-12 py-5 sm:py-6 rounded-full font-semibold glow-gradient-hover transition-all duration-300 border-0 w-full"
                        >
                          Submit Payment Proof
                        </Button>
                      )}
                    </div>
                  </div>
                )}

                {paymentStatus === 'uploading' && (
                  <div className="text-center py-6 sm:py-8">
                    <div className="animate-spin rounded-full h-10 w-10 sm:h-12 sm:w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground text-sm sm:text-base">Submitting...</p>
                  </div>
                )}

                {paymentStatus === 'success' && (
                  <div className="text-center py-6 sm:py-8">
                    <div className="bg-gradient-main w-14 h-14 sm:w-16 sm:h-16 rounded-full flex items-center justify-center mx-auto mb-4 glow-gradient">
                      <CheckCircle2 className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
                    </div>
                    <p className="text-lg sm:text-xl font-bold text-white mb-2">Payment Submitted!</p>
                    <p className="text-sm sm:text-base text-muted-foreground">Check your email: <span className="text-white font-semibold">{userEmail}</span></p>
                    <p className="text-xs text-muted-foreground mt-2">You'll receive your personalized PDF within 24 hours after verification</p>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
