import { FaQuoteLeft, FaQuoteRight } from 'react-icons/fa';
import { useState } from 'react';
import Image from 'next/image'; 

// Define the types for the testimonial data
interface Testimonial {
  name: string;
  quote: string;
}

const Testimonials = () => {
  const testimonials: Testimonial[] = [
    { name: 'Coach Emily R.', quote: 'This platform completely changed the way we analyze our games. Real-time feedback is a game-changer!' },
    { name: 'Athlete Jordan K.', quote: 'I feel safer and more prepared knowing my performance is being tracked and optimized every second.' },
    { name: 'Coach Alex P.', quote: 'Our team’s performance has dramatically improved after implementing this system, and injury rates have gone down.' },
    { name: 'Athlete Sarah W.', quote: 'The insights provided help me to stay focused and improve my technique each day.' },
    { name: 'Coach Tim L.', quote: 'This tool gives us a deep understanding of every player’s strengths and areas for improvement. Truly invaluable.' },
    { name: 'Athlete Lily B.', quote: 'I’ve never felt more prepared for competitions. This system is a game-changer for my training.' }
  ];

  const images = [
    'https://randomuser.me/api/portraits/men/1.jpg',
    'https://randomuser.me/api/portraits/women/2.jpg',
    'https://randomuser.me/api/portraits/men/3.jpg',
    'https://randomuser.me/api/portraits/women/4.jpg',
    'https://randomuser.me/api/portraits/men/5.jpg',
    'https://randomuser.me/api/portraits/women/5.jpg'
  ];

  const [selectedTestimonial, setSelectedTestimonial] = useState<Testimonial | null>(null); // Correct type for selectedTestimonial

  // Function to get a random image
  const getRandomImage = (): string => {
    return images[Math.floor(Math.random() * images.length)];
  };

  const handleClickTestimonial = (testimonial: Testimonial) => {
    setSelectedTestimonial(testimonial); // Open the modal with the clicked testimonial
  };

  const handleCloseModal = () => {
    setSelectedTestimonial(null); // Close the modal
  };

  return (
    <section className="py-20 px-6 bg-neutral-900">
      <div className="max-w-5xl mx-auto text-center">
        <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 tracking-wide">What People Are Saying</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12 md:gap-16">
          {testimonials.map((testimonial, index) => (
            <div
              key={index}
              className="bg-neutral-800 p-8 rounded-2xl shadow-xl hover:scale-105 transition-all transform hover:bg-neutral-700 hover:shadow-2xl relative cursor-pointer"
              onClick={() => handleClickTestimonial(testimonial)} // Open modal on click
            >
              {/* Random Image */}
              <div className="flex justify-center mb-6">
                <Image
                  src={getRandomImage()}
                  alt="testimonial"
                  width={96} // Define width
                  height={96} // Define height
                  className="object-cover rounded-md border-4 border-yellow-400"
                />
              </div>

              {/* Quote */}
              <div className="flex justify-center mb-6">
                <FaQuoteLeft size={40} className="text-yellow-400 animate-pulse" />
              </div>
              <p className="text-gray-300 italic text-lg mb-6">{testimonial.quote}</p>
              <p className="text-yellow-400 text-xl font-semibold">– {testimonial.name}</p>
              <div className="flex justify-center mt-6">
                <FaQuoteRight size={40} className="text-yellow-400 animate-pulse" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal to show the clicked testimonial */}
      {selectedTestimonial && (
        <div
          className="fixed inset-0 bg-gray-900 bg-opacity-70 flex justify-center items-center z-50"
          onClick={handleCloseModal} // Close modal when clicking outside
        >
          <div
            className="bg-neutral-800 p-12 rounded-2xl shadow-xl max-w-xl w-full"
            onClick={(e) => e.stopPropagation()} // Prevent modal from closing when clicking inside it
          >
            {/* Image */}
            <div className="flex justify-center mb-6">
              <Image
                src={getRandomImage()}
                alt="testimonial"
                width={96} // Define width
                height={96} // Define height
                className="object-cover rounded-md border-4 border-yellow-400"
              />
            </div>

            {/* Quote */}
            <div className="flex justify-center mb-6">
              <FaQuoteLeft size={40} className="text-yellow-400 animate-pulse" />
            </div>
            <p className="text-gray-300 italic text-lg mb-6">{selectedTestimonial.quote}</p>
            <p className="text-yellow-400 text-xl font-semibold">– {selectedTestimonial.name}</p>
            <div className="flex justify-center mt-6">
              <FaQuoteRight size={40} className="text-yellow-400 animate-pulse" />
            </div>

            {/* Close button */}
            <button
              className="absolute top-4 right-4 text-yellow-400 text-3xl"
              onClick={handleCloseModal}
            >
              &times;
            </button>
          </div>
        </div>
      )}
    </section>
  );
};

export default Testimonials;
