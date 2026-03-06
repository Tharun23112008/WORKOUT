import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2, Download } from "lucide-react";
import { Button } from "../components/ui/button";
import axios from "axios";

const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL ||
  "https://workout-cwle.onrender.com";

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

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Verifying payment...</p>
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
          <CheckCircle2 className="w-16 h-16 mx-auto mb-6 text-green-500" />

          <h1 className="text-4xl font-bold mb-4">
            Payment Successful
          </h1>

          <p className="text-lg text-muted-foreground mb-10">
            Your personalized 365 Days of Discipline blueprint is ready.
          </p>

          <Button onClick={handleDownload} size="lg">
            <Download className="w-5 h-5 mr-2" />
            Download Your PDF
          </Button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">
          Payment {status === "timeout" ? "Timeout" : "Failed"}
        </h1>

        <p className="text-muted-foreground mb-6">
          Payment verification failed. Please try again.
        </p>

        <Button onClick={() => (window.location.href = "/")}>
          Return Home
        </Button>
      </div>
    </div>
  );
};
