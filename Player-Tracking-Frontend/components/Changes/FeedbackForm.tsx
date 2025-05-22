'use client';

import { useState } from 'react';
import { motion } from 'framer-motion'; 
import { Button } from "@/components/ui/button";



const FeedbackForm = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showThanks, setShowThanks] = useState(false);
  const [errors, setErrors] = useState({ name: '', email: '', feedback: '' });

  const validateForm = () => {
    const newErrors = { name: '', email: '', feedback: '' };
    let isValid = true;

    if (!name.trim()) {
      newErrors.name = 'Name is required.';
      isValid = false;
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required.';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Please enter a valid email address.';
      isValid = false;
    }

    if (!feedback.trim()) {
      newErrors.feedback = 'Feedback is required.';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);

    setTimeout(() => {
      setIsSubmitting(false);
      setShowThanks(true);
    }, 2000);
  };

  return (
    <div className="max-w-lg mx-auto space-y-6">
      {showThanks ? (
        <motion.div
          className="text-center text-neutral-100"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-3xl font-semibold mb-4">Thank you for your feedback!</h2>
          <p className="text-lg text-neutral-300">Your insights are invaluable to us, and we will use them to improve.</p>
        </motion.div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name Box */}
          <motion.div
            className="relative border border-neutral-600 p-4 rounded-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <label htmlFor="name" className="block text-sm font-semibold text-neutral-300 mb-2">Name</label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={`w-full bg-neutral-700 text-neutral-100 text-sm px-4 py-2 rounded-lg border-2 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all ${
                errors.name ? 'border-red-500' : 'border-neutral-700'
              }`}
            />
            {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
          </motion.div>

          {/* Email Box */}
          <motion.div
            className="relative border border-neutral-600 p-4 rounded-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <label htmlFor="email" className="block text-sm font-semibold text-neutral-300 mb-2">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`w-full bg-neutral-700 text-neutral-100 text-sm px-4 py-2 rounded-lg border-2 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all ${
                errors.email ? 'border-red-500' : 'border-neutral-700'
              }`}
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </motion.div>

          {/* Feedback Box */}
          <motion.div
            className="relative border border-neutral-600 p-4 rounded-lg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <label htmlFor="feedback" className="block text-sm font-semibold text-neutral-300 mb-2">Feedback</label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className={`w-full bg-neutral-700 text-neutral-100 text-sm px-4 py-2 rounded-lg border-2 focus:outline-none focus:ring-2 focus:ring-indigo-400 transition-all ${
                errors.feedback ? 'border-red-500' : 'border-neutral-700'
              }`}
            />
            {errors.feedback && <p className="text-red-500 text-xs mt-1">{errors.feedback}</p>}
          </motion.div>

          {/* Submit Button */}
          <motion.div
            className="flex justify-end"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-yellow-400 text-black px-6 py-3 rounded-full hover:bg-yellow-500 transition duration-300 transform hover:scale-105 shadow-lg"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </motion.div>
        </form>
      )}
    </div>
  );
};

export default FeedbackForm;
