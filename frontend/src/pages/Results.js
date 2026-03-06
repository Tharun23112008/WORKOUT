import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, CheckCircle2, X, QrCode, Upload } from "lucide-react";
import { Button } from "../components/ui/button";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";
const API = `${BACKEND_URL}/api`;

export const Results = ({ results, quizId }) => {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentScreenshot, setPaymentScreenshot] = useState(null);
  const [paymentStatus, setPaymentStatus] = useState("pending");
  const [userEmail, setUserEmail] = useState("");
  const [emailError, setEmailError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUnlock = () => {
    setShowPaymentModal(true);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPaymentScreenshot(file);
    }
  };

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleSubmitPayment = async () => {
    if (!validateEmail(userEmail)) {
      setEmailError("Please enter a valid email address");
      return;
    }

    if (!paymentScreenshot) {
      alert("Upload payment screenshot");
      return;
    }

    if (!quizId) {
      alert("Quiz ID missing");
      return;
    }

    setLoading(true);
    setPaymentStatus("uploading");

    try {
      const formData = new FormData();
      formData.append("quiz_id", quizId);
      formData.append("email", userEmail);
      formData.append("screenshot", paymentScreenshot);

      const response = await fetch(`${API}/payment/submit`, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Server error");
      }

      await response.json();

      setPaymentStatus("success");
    } catch (err) {
      console.error(err);
      alert("Payment submission failed. Try again.");
      setPaymentStatus("pending");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen py-20 px-6 relative">
      <div className="max-w-4xl mx-auto">

        <h1 className="text-5xl font-bold text-center mb-6">
          Your Free Snapshot
        </h1>

        <div className="grid sm:grid-cols-2 gap-6 mb-12">
          <div className="text-center">
            <p className="text-sm">DAILY CALORIES</p>
            <p className="text-5xl font-bold">{results.calories}</p>
          </div>

          <div className="text-center">
            <p className="text-sm">PROTEIN TARGET</p>
            <p className="text-5xl font-bold">{results.protein}g</p>
          </div>
        </div>

        <div className="text-center mb-12">
          <p className="text-xl">{results.training_plan}</p>
        </div>

        <div className="text-center">
          <h2 className="text-3xl font-bold mb-6">
            Unlock Full Plan
          </h2>

          <p className="text-lg mb-6">
            Full 365-day workout + nutrition protocol
          </p>

          <div className="mb-6 text-4xl font-bold">
            ₹499
          </div>

          <Button onClick={handleUnlock} size="lg">
            Pay with UPI
          </Button>
        </div>
      </div>

      <AnimatePresence>
        {showPaymentModal && (
          <motion.div
            className="fixed inset-0 bg-black/70 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-white p-8 rounded-xl max-w-lg w-full"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
            >
              <button
                onClick={() => setShowPaymentModal(false)}
                className="float-right"
              >
                <X />
              </button>

              <h2 className="text-2xl font-bold mb-4 text-center">
                Scan to Pay ₹499
              </h2>

              <img
                src="/qr.png"
                alt="QR"
                className="w-64 mx-auto mb-6"
              />

              <input
                type="email"
                placeholder="your@email.com"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                className="w-full border p-3 rounded mb-2"
              />

              {emailError && (
                <p className="text-red-500 text-sm">{emailError}</p>
              )}

              <input
                type="file"
                onChange={handleFileUpload}
                className="w-full mb-4"
              />

              <Button
                onClick={handleSubmitPayment}
                disabled={loading}
                className="w-full"
              >
                Submit Payment Proof
              </Button>

              {paymentStatus === "uploading" && (
                <p className="text-center mt-4">Uploading...</p>
              )}

              {paymentStatus === "success" && (
                <p className="text-center mt-4 text-green-600">
                  Payment submitted. Check your email soon.
                </p>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
