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
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight mb-4 text-center">
            Your Free Snapshot
          </h1>
          <p className="text-center text-muted-foreground mb-12 leading-relaxed">This is 15% of your personalized plan</p>

          {/* Free Preview Section */}
          <div className="bg-card border border-border/40 rounded-2xl p-10 mb-10">
            <div className="grid sm:grid-cols-2 gap-10">
              <div data-testid="calories-display" className="text-center">
                <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-2">DAILY CALORIES</p>
                <p className="text-5xl font-black text-primary">{results.calories}</p>
                <p className="text-sm text-muted-foreground mt-1">kcal per day</p>
              </div>
              <div data-testid="protein-display" className="text-center">
                <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-2">PROTEIN TARGET</p>
                <p className="text-5xl font-black text-primary">{results.protein}g</p>
                <p className="text-sm text-muted-foreground mt-1">per day</p>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-border">
              <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-3">YOUR TRAINING STRUCTURE</p>
              <p className="text-lg font-semibold mb-2">{results.training_plan}</p>
              <p className="text-muted-foreground">Based on your experience and weekly availability</p>
            </div>

            <div className="mt-8 pt-8 border-t border-border">
              <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-3">SAMPLE WORKOUT DAY</p>
              <div className="bg-secondary/50 rounded p-4">
                <p className="font-bold mb-2">Monday: Chest</p>
                <p className="text-sm text-muted-foreground">Bench Press, Incline Dumbbell Press, Cable Flyes...</p>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-border">
              <p className="text-xs uppercase tracking-[0.2em] font-bold text-accent mb-3">SAMPLE MEAL IDEA</p>
              <div className="bg-secondary/50 rounded p-4">
                <p className="text-sm text-muted-foreground">Breakfast: Eggs with whole grain toast and avocado (approx. {Math.round(results.calories * 0.25)} kcal)</p>
              </div>
            </div>
          </div>

          {/* Paywall Section */}
          <div className="bg-gradient-to-b from-card to-secondary border-2 border-primary/30 rounded-2xl p-10 relative overflow-hidden glow-purple">
            <div className="absolute top-4 right-4">
              <Lock className="w-8 h-8 text-primary" />
            </div>
            
            <h2 className="text-2xl font-bold tracking-tight mb-4">Unlock Your Full Protocol</h2>
            <p className="text-muted-foreground mb-8 leading-relaxed">Get the complete 365 Days of Discipline blueprint</p>

            <div className="space-y-3 mb-8">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Complete 7-day training routine with exercise selection</p>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Detailed sets, reps, rest times, and execution cues</p>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Full nutrition guide with meal timing and sample plans</p>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Active rest protocol for faster recovery</p>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Common mistakes to avoid and discipline reminders</p>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
                <p className="text-sm">Exportable high-quality PDF for offline use</p>
              </div>
            </div>

            <div className="text-center">
              <div className="mb-4">
                <span className="text-4xl font-black text-primary">₹499</span>
                <span className="text-muted-foreground ml-2">one-time</span>
              </div>
              <Button
                data-testid="unlock-pdf-btn"
                onClick={handleUnlock}
                disabled={loading}
                size="lg"
                className="bg-primary hover:bg-primary/90 text-white text-base px-12 py-6 rounded-full font-semibold w-full sm:w-auto glow-purple-hover transition-all duration-300"
              >
                {loading ? 'Processing...' : 'Unlock Full Blueprint'}
              </Button>
              <p className="text-xs text-muted-foreground mt-3">Secure payment via Stripe</p>
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