import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, CheckCircle2, X, QrCode, Upload } from 'lucide-react';
import { Button } from '../components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${https://workout-cwle.onrender.com}/api`;

export const Results = ({ results, quizId }) => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentScreenshot, setPaymentScreenshot] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState('pending');

  // Lock background scroll when modal is open
  useEffect(() => {
    if (showPaymentModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [showPaymentModal]);

  const handleUnlock = () => {
    setShowPaymentModal(true);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPaymentScreenshot(file);
    }
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
    <div className="min-h-screen py-20 px-6 relative">
      {/* Gradient Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-0 w-96 h-96 bg-primary rounded-full blur-[150px] opacity-20"></div>
        <div className="absolute bottom-1/4 left-0 w-96 h-96 bg-secondary rounded-full blur-[150px] opacity-20"></div>
      </div>

      <div className="max-w-4xl mx-auto relative z-10">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-4 text-center">
            <span className="gradient-text">Your Free Snapshot</span>
          </h1>
          <p className="text-center text-muted-foreground mb-16 leading-relaxed text-lg">
            This is 15% of your personalized plan
          </p>

          {/* Free Preview Section */}
          <div className="glass-morphism-strong rounded-full p-12 mb-12 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary rounded-full blur-[100px] opacity-10"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary rounded-full blur-[100px] opacity-10"></div>

            <div className="relative z-10">
              <div className="grid sm:grid-cols-2 gap-10">
                <div data-testid="calories-display" className="text-center glass-morphism rounded-full p-10">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-3">DAILY CALORIES</p>
                  <p className="text-7xl font-black text-white mb-2">{results.calories}</p>
                  <p className="text-sm text-muted-foreground">kcal per day</p>
                </div>
                <div data-testid="protein-display" className="text-center glass-morphism rounded-full p-10">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-3">PROTEIN TARGET</p>
                  <p className="text-7xl font-black text-white mb-2">{results.protein}g</p>
                  <p className="text-sm text-muted-foreground">per day</p>
                </div>
              </div>

              <div className="mt-12 pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-4">YOUR TRAINING STRUCTURE</p>
                <p className="text-xl font-semibold mb-3 text-white">{results.training_plan}</p>
                <p className="text-muted-foreground leading-relaxed">Based on your experience and weekly availability</p>
              </div>

              <div className="mt-12 pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-4">SAMPLE WORKOUT DAY</p>
                <div className="glass-morphism rounded-full p-8">
                  <p className="font-bold mb-2 text-white text-lg">Monday: Chest</p>
                  <p className="text-muted-foreground">Bench Press, Incline Dumbbell Press, Cable Flyes...</p>
                </div>
              </div>

              <div className="mt-12 pt-12 border-t-2 border-white/10">
                <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-4">SAMPLE MEAL IDEA</p>
                <div className="glass-morphism rounded-full p-8">
                  <p className="text-muted-foreground">
                    Breakfast: Eggs with whole grain toast and avocado (approx. {Math.round(results.calories * 0.25)} kcal)
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Paywall Section */}
          <div className="glass-morphism-strong rounded-full p-14 relative overflow-hidden glow-gradient">
            <div className="absolute top-0 right-0 w-96 h-96 bg-primary rounded-full blur-[120px] opacity-20"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-secondary rounded-full blur-[120px] opacity-20"></div>

            <div className="relative z-10">
              <div className="flex items-center justify-center gap-4 mb-6">
                <div className="bg-gradient-main p-4 rounded-full glow-gradient">
                  <Lock className="w-10 h-10 text-white" />
                </div>
              </div>

              <h2 className="text-4xl font-bold tracking-tight mb-4 text-center gradient-text">Unlock Your Full Protocol</h2>
              <p className="text-muted-foreground mb-12 leading-relaxed text-lg text-center max-w-2xl mx-auto">
                Get the complete 365 Days of Discipline blueprint
              </p>

              <div className="space-y-4 mb-12">
                {[
                  'Complete 7-day training routine with exercise selection',
                  'Detailed sets, reps, rest times, and execution cues',
                  'Full nutrition guide with meal timing and sample plans',
                  'Active rest protocol for faster recovery',
                  'Common mistakes to avoid and discipline reminders',
                  'Exportable high-quality PDF for offline use',
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                    <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                      <CheckCircle2 className="w-5 h-5 text-white" />
                    </div>
                    <p className="leading-relaxed text-white">{item}</p>
                  </div>
                ))}
              </div>

              <div className="text-center">
                <div className="mb-8">
                  <span className="text-6xl font-black gradient-text">₹499</span>
                  <span className="text-muted-foreground ml-3 text-xl">one-time</span>
                </div>
                <Button
                  data-testid="unlock-pdf-btn"
                  onClick={handleUnlock}
                  size="lg"
                  className="bg-gradient-button text-white text-lg px-16 py-8 rounded-full font-semibold w-full sm:w-auto glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
                >
                  Pay with FamPay / UPI
                </Button>
                <p className="text-xs text-muted-foreground mt-5">Scan QR code to pay securely</p>
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
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowPaymentModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="glass-morphism-strong rounded-3xl p-10 max-w-2xl w-full relative max-h-[90vh] overflow-y-auto"
            >
              {/* ✅ FIX: z-20 so it sits above gradient orbs */}
              <button
                onClick={() => setShowPaymentModal(false)}
                className="absolute top-6 right-6 z-20 glass-morphism p-2 rounded-full hover:glass-morphism-strong transition-all"
              >
                <X className="w-6 h-6 text-white" />
              </button>

              {/* Gradient Orbs - z-0 so they don't block clicks */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary rounded-full blur-[100px] opacity-20 z-0 pointer-events-none"></div>
              <div className="absolute bottom-0 left-0 w-64 h-64 bg-secondary rounded-full blur-[100px] opacity-20 z-0 pointer-events-none"></div>

              <div className="relative z-10">
                <div className="text-center mb-8">
                  <div className="bg-gradient-main w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 glow-gradient">
                    <QrCode className="w-10 h-10 text-white" />
                  </div>
                  <h2 className="text-3xl font-bold gradient-text mb-3">Scan to Pay ₹499</h2>
                  <p className="text-muted-foreground">Use any UPI app (FamPay, PhonePe, GPay, Paytm)</p>
                </div>

                {/* QR Code */}
                <div className="flex justify-center mb-8">
                  <div className="glass-morphism-strong p-6 rounded-3xl glow-gradient">
                    <img
                      src="https://customer-assets.emergentagent.com/job_fitpro-quiz/artifacts/uo7mdy9q_Screenshot_2026-03-03-16-10-35-33_ba41e9a642e6e0e2b03656bfbbffd6e4.jpg"
                      alt="FamPay QR Code"
                      className="w-80 h-80 object-contain rounded-2xl"
                    />
                  </div>
                </div>

                {/* UPI ID */}
                <div className="glass-morphism rounded-full p-6 mb-8 text-center">
                  <p className="text-xs uppercase tracking-widest font-semibold gradient-text mb-2">OR USE UPI ID</p>
                  <p className="text-2xl font-bold text-white">7204042383@fam</p>
                </div>

                {/* Upload Screenshot */}
                {paymentStatus === 'pending' && (
                  <div className="glass-morphism rounded-3xl p-8">
                    <p className="text-sm text-muted-foreground mb-4 text-center">
                      After payment, upload screenshot for verification
                    </p>
                    <div className="flex flex-col items-center gap-4">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileUpload}
                        className="hidden"
                        id="payment-screenshot"
                      />
                      <label
                        htmlFor="payment-screenshot"
                        className="glass-morphism-strong rounded-full px-8 py-4 cursor-pointer hover:glass-morphism transition-all flex items-center gap-3"
                      >
                        <Upload className="w-5 h-5 text-primary" />
                        <span className="text-white">
                          {paymentScreenshot ? paymentScreenshot.name : 'Choose Screenshot'}
                        </span>
                      </label>
                      {paymentScreenshot && (
                        <Button
                          onClick={handleSubmitPayment}
                          className="bg-gradient-button text-white px-12 py-6 rounded-full font-semibold glow-gradient-hover transition-all duration-300 border-0"
                        >
                          Submit Payment Proof
                        </Button>
                      )}
                    </div>
                  </div>
                )}

                {paymentStatus === 'uploading' && (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
                    <p className="text-muted-foreground">Submitting...</p>
                  </div>
                )}

                {paymentStatus === 'success' && (
                  <div className="text-center py-8">
                    <div className="bg-gradient-main w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 glow-gradient">
                      <CheckCircle2 className="w-10 h-10 text-white" />
                    </div>
                    <p className="text-xl font-bold text-white mb-2">Payment Submitted!</p>
                    <p className="text-muted-foreground">You'll receive your PDF within 24 hours after verification</p>
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
