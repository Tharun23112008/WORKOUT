import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, Lock } from 'lucide-react';
import { Button } from '../components/ui/button';

export const Landing = ({ onStart }) => {
  return (
    <div className="min-h-screen noise-bg relative">
      {/* Hero Section */}
      <div 
        className="min-h-screen flex items-center justify-center relative"
        style={{
          backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.85)), url('https://images.unsplash.com/photo-1740895307943-7878df384db1?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAzNTl8MHwxfHNlYXJjaHwzfHxneW0lMjB3b3Jrb3V0JTIwZGFyayUyMGxpZ2h0aW5nfGVufDB8fHx8MTc3MjUyODQ3OHww&ixlib=rb-4.1.0&q=85')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      >
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-tight text-white mb-6">
              365 Days of<br/>Discipline
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
              Built from a real one-year transformation. Get your personalized training and nutrition blueprint in 3 minutes.
            </p>
            <Button 
              data-testid="start-quiz-btn"
              onClick={onStart}
              size="lg"
              className="bg-primary hover:bg-primary/90 text-white text-base px-10 py-6 rounded-full font-semibold glow-purple-hover transition-all duration-300"
            >
              Start Your Protocol
            </Button>
          </motion.div>
        </div>
      </div>

      {/* Why This System Exists */}
      <div className="py-32 px-6 max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="bg-card/50 border border-border/30 rounded-2xl p-12"
        >
          <h2 className="text-2xl font-bold mb-6 text-center">Why This System Exists</h2>
          <p className="text-muted-foreground leading-relaxed text-center">
            I followed a bro split for 365 days without missing a session. No program hopping, no overthinking. Just consistency. The results came not from complexity, but from showing up. I built this system because most people need personalized targets and a simple structure, not more information. This isn't about motivation—it's about giving you clarity on what to eat, how to train, and why discipline matters more than intensity. Use it for at least 12 weeks before changing anything.
          </p>
        </motion.div>
      </div>

      {/* Features Grid */}
      <div className="py-24 px-6 max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-card border border-border/40 hover:border-primary/50 transition-all duration-300 rounded-2xl p-10"
          >
            <Activity className="w-12 h-12 text-primary mb-6" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold mb-4">Personalized Calculation</h3>
            <p className="text-muted-foreground leading-relaxed">Exact calories, protein, and macros based on your body and goals.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="bg-card border border-border/40 hover:border-primary/50 transition-all duration-300 rounded-2xl p-10"
          >
            <Zap className="w-12 h-12 text-accent mb-6" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold mb-4">Bro Split System</h3>
            <p className="text-muted-foreground leading-relaxed">Proven 6-day training split. Chest, Back, Shoulders, Biceps, Triceps, Legs.</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="bg-card border border-border/40 hover:border-primary/50 transition-all duration-300 rounded-2xl p-10"
          >
            <Lock className="w-12 h-12 text-primary mb-6" strokeWidth={1.5} />
            <h3 className="text-xl font-semibold mb-4">Full PDF Blueprint</h3>
            <p className="text-muted-foreground leading-relaxed">Complete training routine, nutrition guide, and recovery protocol.</p>
          </motion.div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-32 px-6 text-center">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">Ready to Start?</h2>
          <p className="text-lg text-muted-foreground mb-10 leading-relaxed">Answer 11 questions. Get your personalized protocol.</p>
          <Button 
            data-testid="cta-start-btn"
            onClick={onStart}
            size="lg"
            className="bg-primary hover:bg-primary/90 text-white text-base px-10 py-6 rounded-full font-semibold glow-purple-hover transition-all duration-300"
          >
            Begin Quiz
          </Button>
        </motion.div>
      </div>
    </div>
  );
};
