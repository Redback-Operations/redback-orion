'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';
import { Button } from "@/components/ui/button";

const StarRating = () => {
  const [rating, setRating] = useState<number | null>(null);
  const [hover, setHover] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const activeValue = hover !== null ? hover : rating;

  const handleSubmit = () => {
    if (rating === null) return;
    setSubmitted(true);
  };

  return (
    <div className="max-w-lg mx-auto mt-12 bg-gradient-to-br from-neutral-800 to-neutral-900 border border-neutral-700 rounded-3xl shadow-2xl p-8 text-center space-y-6">
      {submitted ? (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-neutral-100"
        >
          <h2 className="text-3xl font-bold mb-2">Thanks for rating! 🎉</h2>
          {rating !== null && (
            <p className="text-neutral-400">
              You rated us {rating} out of 5 stars.
            </p>
          )}
        </motion.div>
      ) : (
        <>
          <motion.h3
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl font-semibold text-yellow-400"
          >
            Rate your experience
          </motion.h3>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex justify-center gap-3"
          >
            {[1, 2, 3, 4, 5].map((star) => (
              <Star
                key={star}
                size={36}
                className={`cursor-pointer transition-colors duration-200 ${
                  activeValue !== null && activeValue >= star
                    ? 'text-yellow-400'
                    : 'text-neutral-600'
                }`}
                onMouseEnter={() => setHover(star)}
                onMouseLeave={() => setHover(null)}
                onClick={() => setRating(star)}
                fill={activeValue !== null && activeValue >= star ? '#facc15' : 'none'}
              />
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <Button
              onClick={handleSubmit}
              disabled={rating === null}
              className="mt-4 bg-yellow-400 text-black hover:bg-yellow-500 transition hover:scale-105 rounded-full px-6 py-2.5"
            >
              Submit Rating
            </Button>
          </motion.div>
        </>
      )}
    </div>
  );
};

export default StarRating;
