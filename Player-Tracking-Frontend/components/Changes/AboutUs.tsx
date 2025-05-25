// /components/AboutUs.js
import { useState } from 'react';
import { Button } from "@/components/ui/button"; 
import { motion } from 'framer-motion';  

const AboutUs = () => {
  const [showMore, setShowMore] = useState(false);

  // Toggle the description content
  const toggleDescription = () => {
    setShowMore(!showMore);
  };

  return (
    <section className="py-20 px-6 bg-neutral-900">
      <div className="max-w-5xl mx-auto text-center">
        {/* Header */}
        <motion.h2
          className="text-4xl font-bold text-yellow-400 mb-6"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          About Us
        </motion.h2>

        {/* Main Content Box */}
        <motion.div
          className="bg-neutral-800 p-8 rounded-lg shadow-lg mb-8 transition duration-300 transform hover:scale-105 hover:shadow-2xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2 }}
        >
          <p className="text-gray-300 text-lg mb-4">
            At Orion Labs, we transform sports tracking with cutting-edge technology—delivering real-time video insights, dynamic pose estimation, and data-driven precision to elevate every game. Our innovative system seamlessly integrates into practical applications, providing tangible value that redefines athletic performance.
          </p>
        </motion.div>

        {/* Additional Description Box (Visible when 'Learn More' is clicked) */}
        {showMore && (
          <motion.div
            className="bg-neutral-800 p-8 rounded-lg shadow-lg mb-8 transition duration-300 transform hover:scale-105 hover:shadow-2xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.2 }}
          >
            <p className="text-gray-300 text-lg">
              We aim to bridge the gap between technology and sports. Our system not only offers real-time performance metrics but also continuously learns and adapts, optimizing every aspect of an athlete’s game. Whether on the field, court, or track, Orion Labs is revolutionizing how coaches and athletes interact with data.
            </p>
          </motion.div>
        )}

        {/* Learn More / Show Less Button */}
        <Button
          onClick={toggleDescription}
          className="bg-yellow-400 text-black px-6 py-3 rounded-full hover:bg-yellow-500 transition duration-300 transform hover:scale-105 shadow-lg"
        >
          {showMore ? 'Show Less' : 'Learn More'}
        </Button>
      </div>
    </section>
  );
};

export default AboutUs;
