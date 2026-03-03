import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, Lock } from 'lucide-react';
import { Button } from '../components/ui/button';

export const Landing = ({ onStart }) => {
  return (
    <div className="min-h-screen relative bg-black">
      {/* Gradient Background Orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary rounded-full blur-[150px] opacity-20"></div>
        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-secondary rounded-full blur-[150px] opacity-20"></div>
      </div>

      {/* Hero Section */}
      <div className="relative min-h-screen flex items-center justify-center">
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-block glass-morphism rounded-full px-6 py-2 mb-8">
              <p className="text-sm font-semibold gradient-text">COMING SOON</p>
            </div>
            
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-bold tracking-tight leading-tight mb-6">
              365 Days of<br/>
              <span className="gradient-text">Discipline</span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
              Built from a real one-year transformation. Get your personalized training and nutrition blueprint in 3 minutes.
            </p>
            
            <Button 
              data-testid="start-quiz-btn"
              onClick={onStart}
              size="lg"
              className="bg-gradient-button text-white text-lg px-14 py-8 rounded-full font-semibold glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
            >
              Start Your Protocol
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Why This System Exists */}
      <div className="relative py-32 px-6 max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass-morphism-strong rounded-3xl p-14"
        >
          <h2 className="text-3xl font-bold mb-6 text-center gradient-text">Why This System Exists</h2>
          <p className="text-muted-foreground leading-relaxed text-center text-lg">
            I followed a bro split for 365 days without missing a session. No program hopping, no overthinking. Just consistency. The results came not from complexity, but from showing up. I built this system because most people need personalized targets and a simple structure, not more information. This isn't about motivation—it's about giving you clarity on what to eat, how to train, and why discipline matters more than intensity. Use it for at least 12 weeks before changing anything.
          </p>
        </motion.div>
      </div>

      {/* Features Grid */}
      <div className="relative py-24 px-6 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="glass-morphism hover:glass-morphism-strong transition-all duration-300 rounded-full p-12 text-center group"
          >
            <div className="bg-gradient-main w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 glow-gradient">
              <Activity className="w-10 h-10 text-white" strokeWidth={2} />
            </div>
            <h3 className="text-2xl font-semibold mb-4 text-white">Personalized Calculation</h3>
            <p className="text-muted-foreground leading-relaxed">Exact calories, protein, and macros based on your body and goals.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="glass-morphism hover:glass-morphism-strong transition-all duration-300 rounded-full p-12 text-center group"
          >
            <div className="bg-gradient-main w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 glow-gradient">
              <Zap className="w-10 h-10 text-white" strokeWidth={2} />
            </div>
            <h3 className="text-2xl font-semibold mb-4 text-white">Bro Split System</h3>
            <p className="text-muted-foreground leading-relaxed">Proven 6-day training split. Chest, Back, Shoulders, Biceps, Triceps, Legs.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="glass-morphism hover:glass-morphism-strong transition-all duration-300 rounded-full p-12 text-center group"
          >
            <div className="bg-gradient-main w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 glow-gradient">
              <Lock className="w-10 h-10 text-white" strokeWidth={2} />
            </div>
            <h3 className="text-2xl font-semibold mb-4 text-white">Full PDF Blueprint</h3>
            <p className="text-muted-foreground leading-relaxed">Complete training routine, nutrition guide, and recovery protocol.</p>
          </motion.div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative py-32 px-6 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-5xl sm:text-6xl font-bold tracking-tight mb-6">
            Ready to <span className="gradient-text">Start?</span>
          </h2>
          <p className="text-xl text-muted-foreground mb-12 leading-relaxed">Answer 11 questions. Get your personalized protocol.</p>
          <Button 
            data-testid="cta-start-btn"
            onClick={onStart}
            size="lg"
            className="bg-gradient-button text-white text-lg px-14 py-8 rounded-full font-semibold glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
          >
            Begin Quiz
          </Button>
        </motion.div>
      </div>
    </div>
  );
};
