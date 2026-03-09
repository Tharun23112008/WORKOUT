import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Download, XCircle, Clock } from "lucide-react";
import { Button } from "../components/ui/button";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "https://workout-cwle.onrender.com";
const API = `${BACKEND_URL}/api`;

export const Success = () => {
  const [status, setStatus] = useState("checking");
  const [quizId, setQuizId] = useState(null);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("session_id");

    if (!sessionId) {
      setStatus("failed");
      return;
    }

    let attempts = 0;
    const maxAttempts = 5;

    const checkPaymentStatus = async () => {
      try {
        const response = await axios.get(`${API}/checkout/status/${sessionId}`);
        if (response.data.payment_status === "paid") {
          setStatus("success");
          setQuizId(response.data.metadata.quiz_id);
          return;
        }
        if (response.data.status === "expired") {
          setStatus("failed");
          return;
        }
        attempts++;
        if (attempts >= maxAttempts) {
          setStatus("timeout");
          return;
        }
        setTimeout(checkPaymentStatus, 2000);
      } catch (error) {
        console.error("Payment status error:", error);
        setStatus("error");
      }
    };

    checkPaymentStatus();
  }, []);

  const handleDownload = () => {
    if (!quizId) return;
    window.open(`${API}/pdf/download/${quizId}`, "_blank");
  };

  // Checking / Loading State
  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 relative">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-primary rounded-full blur-[150px] opacity-20"></div>
          <div className="absolute bottom-0 left-0 w-64 sm:w-96 h-64 sm:h-96 bg-secondary rounded-full blur-[150px] opacity-20"></div>
        </div>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center relative z-10"
        >
          <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-t-2 border-b-2 border-primary mx-auto mb-6"></div>
          <p className="text-base sm:text-lg text-muted-foreground">Verifying payment...</p>
        </motion.div>
      </div>
    );
  }

  // Success State
  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 relative">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-primary rounded-full blur-[150px] opacity-20"></div>
          <div className="absolute bottom-0 left-0 w-64 sm:w-96 h-64 sm:h-96 bg-secondary rounded-full blur-[150px] opacity-20"></div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl w-full text-center relative z-10"
        >
          <div className="glass-morphism-strong rounded-2xl sm:rounded-3xl p-8 sm:p-14 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-primary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>

            <div className="relative z-10">
              <div className="bg-gradient-main w-16 h-16 sm:w-24 sm:h-24 rounded-full flex items-center justify-center mx-auto mb-6 sm:mb-8 glow-gradient">
                <CheckCircle2 className="w-8 h-8 sm:w-12 sm:h-12 text-white" />
              </div>

              <h1 className="text-3xl sm:text-5xl font-bold mb-3 sm:mb-4 gradient-text">
                Payment Successful
              </h1>

              <p className="text-sm sm:text-lg text-muted-foreground mb-8 sm:mb-10 leading-relaxed max-w-md mx-auto">
                Your personalized 365 Days of Discipline blueprint is ready to download.
              </p>

              <Button
                onClick={handleDownload}
                size="lg"
                className="bg-gradient-button text-white text-base sm:text-lg px-10 sm:px-14 py-5 sm:py-8 rounded-full font-semibold glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0 w-full sm:w-auto"
              >
                <Download className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                Download Your PDF
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Failed / Timeout / Error State
  const isTimeout = status === "timeout";
  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 relative">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-primary rounded-full blur-[150px] opacity-20"></div>
        <div className="absolute bottom-0 left-0 w-64 sm:w-96 h-64 sm:h-96 bg-secondary rounded-full blur-[150px] opacity-20"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full text-center relative z-10"
      >
        <div className="glass-morphism-strong rounded-2xl sm:rounded-3xl p-8 sm:p-14 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-primary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary rounded-full blur-[100px] opacity-10 pointer-events-none"></div>

          <div className="relative z-10">
            <div className="bg-white/10 w-16 h-16 sm:w-24 sm:h-24 rounded-full flex items-center justify-center mx-auto mb-6 sm:mb-8">
              {isTimeout
                ? <Clock className="w-8 h-8 sm:w-12 sm:h-12 text-yellow-400" />
                : <XCircle className="w-8 h-8 sm:w-12 sm:h-12 text-red-400" />
              }
            </div>

            <h1 className="text-2xl sm:text-4xl font-bold mb-3 sm:mb-4 text-white">
              Payment {isTimeout ? "Timed Out" : "Failed"}
            </h1>

            <p className="text-sm sm:text-base text-muted-foreground mb-8 sm:mb-10 leading-relaxed max-w-md mx-auto">
              {isTimeout
                ? "Verification took too long. If you completed payment, please contact support."
                : "Payment verification failed. Please try again or contact support."
              }
            </p>

            <Button
              onClick={() => (window.location.href = "/")}
              size="lg"
              className="bg-gradient-button text-white text-base sm:text-lg px-10 sm:px-14 py-5 sm:py-8 rounded-full font-semibold glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0 w-full sm:w-auto"
            >
              Return Home
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
