import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Download } from "lucide-react";
import { Button } from "../components/ui/button";
import axios from "axios";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || "https://YOUR-RENDER-BACKEND-URL.onrender.com";

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

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Verifying your payment...</p>
        </div>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-2xl text-center"
        >
          <div className="bg-gradient-main w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-8 glow-gradient">
            <CheckCircle2 className="w-14 h-14 text-white" strokeWidth={2} />
          </div>

          <h1 className="text-5xl sm:text-6xl font-bold mb-4">
            <span className="gradient-text">Payment Successful</span>
          </h1>

          <p className="text-xl text-muted-foreground mb-12">
            Your personalized 365 Days of Discipline blueprint is ready.
          </p>

          <Button
            onClick={handleDownload}
            size="lg"
            className="bg-gradient-button text-white text-lg px-14 py-8 rounded-full"
          >
            <Download className="w-6 h-6 mr-2" />
            Download Your PDF
          </Button>

          <div className="mt-16 glass-morphism-strong rounded-full p-10">
            <p className="text-sm text-muted-foreground mb-3">Remember:</p>
            <p className="font-semibold text-lg text-white">
              Consistency beats perfection. Follow this plan for 8–12 weeks.
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold mb-4">
          Payment {status === "timeout" ? "Timeout" : "Failed"}
        </h1>

        <p className="text-muted-foreground mb-6">
          {status === "timeout"
            ? "Payment verification timed out. Please check your email."
            : "Payment was not successful. Please try again."}
        </p>

        <Button onClick={() => (window.location.href = "/")} variant="outline">
          Return Home
        </Button>
      </div>
    </div>
  );
};
            size="lg"
            className="bg-gradient-button text-white text-lg px-14 py-8 rounded-full font-semibold glow-gradient-hover transition-all duration-300 transform hover:scale-105 border-0"
          >
            <Download className="w-6 h-6 mr-2" />
            Download Your PDF
          </Button>

          <div className="mt-16 glass-morphism-strong rounded-full p-10">
            <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
              Remember:
            </p>
            <p className="font-semibold leading-relaxed text-lg text-white">
              Consistency beats perfection. Follow this plan for at least 8–12
              weeks.
            </p>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-bold mb-4">
          Payment {status === "timeout" ? "Timeout" : "Failed"}
        </h1>

        <p className="text-muted-foreground mb-6">
          {status === "timeout"
            ? "Payment verification timed out. Please check your email or contact support."
            : "Payment was not successful. Please try again."}
        </p>

        <Button onClick={() => (window.location.href = "/")} variant="outline">
          Return Home
        </Button>
      </div>
    </div>
  );
};
