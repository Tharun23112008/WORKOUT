import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
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
    if (file) setPaymentScreenshot(file);
  };

  const validateEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  const handleSubmitPayment = async () => {
    if (!validateEmail(userEmail)) {
      setEmailError("Enter a valid email");
      return;
    }

    if (!paymentScreenshot) {
      alert("Upload payment screenshot");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("quiz_id", quizId);
      formData.append("email", userEmail);
      formData.append("screenshot", paymentScreenshot);

      const res = await fetch(`${API}/payment/submit`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Server error");

      setPaymentStatus("success");
    } catch (err) {
      alert("Payment submission failed");
      setPaymentStatus("pending");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen py-16 px-5 bg-black text-white">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl md:text-5xl font-bold text-center mb-10">
          Your Free Snapshot
        </h1>

        {/* CALORIES + PROTEIN */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 mb-12">
          <div className="bg-white/5 p-8 rounded-2xl text-center">
            <p className="text-xs uppercase tracking-wider text-gray-400">
              Daily Calories
            </p>
            <p className="text-4xl md:text-5xl font-bold mt-2">
              {results?.calories || "..."}
            </p>
            <p className="text-sm text-gray-400 mt-2">kcal per day</p>
          </div>

          <div className="bg-white/5 p-8 rounded-2xl text-center">
            <p className="text-xs uppercase tracking-wider text-gray-400">
              Protein Target
            </p>
            <p className="text-4xl md:text-5xl font-bold mt-2">
              {results?.protein || "..."}g
            </p>
            <p className="text-sm text-gray-400 mt-2">per day</p>
          </div>
        </div>

        {/* TRAINING PREVIEW */}
        <div className="bg-white/5 p-6 rounded-xl text-center mb-12">
          <p className="text-sm text-gray-400 mb-2">Your Training Structure</p>
          <p className="text-lg md:text-xl">
            {results?.training_plan || "Custom training split"}
          </p>
        </div>

        {/* PAYWALL */}
        <div className="text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            Unlock the Full 365-Day Protocol
          </h2>
          <p className="text-gray-400 mb-6 max-w-lg mx-auto">
            Complete workout system, nutrition plan, recovery protocols, and a
            downloadable PDF blueprint.
          </p>
          <div className="text-3xl font-bold mb-6">₹499 one-time</div>
          <Button onClick={handleUnlock} size="lg">
            Unlock Full Plan
          </Button>
        </div>
      </div>

      {/* PAYMENT MODAL */}
      <AnimatePresence>
        {showPaymentModal && (
          <motion.div
            className="fixed inset-0 bg-black/80 flex items-center justify-center p-6 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowPaymentModal(false)}
          >
            <motion.div
              className="bg-white text-black p-8 rounded-2xl max-w-md w-full relative max-h-[90vh] overflow-y-auto"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* X Button */}
              <button
                onClick={() => setShowPaymentModal(false)}
                className="absolute top-4 right-4 z-10 bg-gray-100 hover:bg-gray-200 rounded-full p-1"
              >
                <X size={20} />
              </button>

              <h2 className="text-2xl font-bold text-center mb-6">
                Scan to Pay ₹499
              </h2>

              <img
                src="/qr.png"
                alt="QR"
                className="w-56 mx-auto mb-6"
              />

              <input
                type="email"
                placeholder="your@email.com"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                className="w-full border p-3 rounded mb-2"
              />

              {emailError && (
                <p className="text-red-500 text-sm mb-2">{emailError}</p>
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
