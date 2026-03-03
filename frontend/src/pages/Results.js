import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Lock, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Results = ({ results, quizId, onUnlock }) => {
  const [loading, setLoading] = useState(false);

  const handleUnlock = async () => {
    setLoading(true);
    try {
      const originUrl = window.location.origin;
      const response = await axios.post(`${API}/checkout/session`, {
        quiz_id: quizId,
        origin_url: originUrl,
      });
      // Redirect to Stripe
      window.location.href = response.data.url;
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Failed to initiate payment. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-20 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-4 text-center">
            <span className="gradient-text">Your Free Snapshot</span>
          </h1>
          <p className="text-center text-muted-foreground mb-16 leading-relaxed text-lg">This is 15% of your personalized plan</p>

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
                <p className="text-muted-foreground">Breakfast: Eggs with whole grain toast and avocado (approx. {Math.round(results.calories * 0.25)} kcal)</p>
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
              <p className="text-muted-foreground mb-12 leading-relaxed text-lg text-center max-w-2xl mx-auto">Get the complete 365 Days of Discipline blueprint</p>

            <div className="space-y-4 mb-12">
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Complete 7-day training routine with exercise selection</p>
              </div>
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Detailed sets, reps, rest times, and execution cues</p>
              </div>
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Full nutrition guide with meal timing and sample plans</p>
              </div>
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Active rest protocol for faster recovery</p>
              </div>
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Common mistakes to avoid and discipline reminders</p>
              </div>
              <div className="flex items-start gap-4 glass-morphism rounded-full p-6 hover:glass-morphism-strong transition-all">
                <div className="bg-gradient-main p-2 rounded-full flex-shrink-0">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <p className="leading-relaxed text-white">Exportable high-quality PDF for offline use</p>
              </div>
            </div>

            <div className="text-center">
              <div className="mb-8">
                <span className="text-6xl font-black gradient-text">₹499</span>
                <span className="text-muted-foreground ml-3 text-xl">one-time</span>
              </div>
              <Button
                data-testid="unlock-pdf-btn"
                onClick={handleUnlock}
                disabled={loading}
                size="lg"
                className="bg-gradient-button text-white text-lg px-16 py-8 rounded-full font-semibold w-full sm:w-auto glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
              >
                {loading ? 'Processing...' : 'Unlock Full Blueprint'}
              </Button>
              <p className="text-xs text-muted-foreground mt-5">Secure payment via Stripe</p>
            </div>
            </div>
          </div>

          {/* Blurred Preview */}
          <div className="mt-8 blur-paywall">
            <div className="bg-card border border-border/40 rounded-lg p-8">
              <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-3">FULL TRAINING BREAKDOWN</p>
              <div className="space-y-2">
                <p>Monday: Chest - Complete exercise list with sets/reps</p>
                <p>Tuesday: Back - Complete exercise list with sets/reps</p>
                <p>Wednesday: Shoulders - Complete exercise list...</p>
                <p>And much more detailed guidance...</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};