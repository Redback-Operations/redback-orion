'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import Image from 'next/image';
import Link from 'next/link';

import FeedbackForm from '@/components/Changes/FeedbackForm';
import Testimonials from '@/components/Changes/Testimonials';
import WhyChooseUs from '@/components/Changes/WhyChooseUs';
import BlogSection from '@/components/Changes/BlogSection';
import AwardsSection from '@/components/Changes/AwardsSection';
import FAQSection from '@/components/Changes/FAQSection';
import StarRating from '@/components/Changes/StarRating';
import AboutUs from '@/components/Changes/AboutUs';
import ChatBot from '@/components/Changes/ChatBot';

import { FaTwitter, FaLinkedin, FaGithub, FaFacebook } from 'react-icons/fa';

export default function Home() {
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const toggleFeedbackForm = () => setIsFeedbackOpen(!isFeedbackOpen);

  return (
    <>
      <main className="min-h-screen bg-black text-white">
        {/* Hero Section */}
        <section className="pt-40 pb-20 px-6">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl sm:text-6xl font-extrabold leading-tight tracking-tight mb-6">
                Smarter Player Tracking
              </h1>
              <p className="text-lg text-gray-400 mb-8 max-w-xl">
                Real-time insights for athletes and coaches. Optimize performance, reduce injury risks, and elevate game strategy with intelligent data.
              </p>
              <div className="flex flex-wrap gap-4">
                <Button className="bg-yellow-400 text-black px-6 py-3 rounded-full hover:bg-yellow-500 transition">
                  Get Started
                </Button>
                <Button variant="outline" className="border-yellow-400 text-yellow-400 px-6 py-3 rounded-full hover:bg-yellow-400 hover:text-black transition">
                  Learn More
                </Button>
              </div>
            </div>
            <div className="relative h-[400px] sm:h-[500px]">
              <Image
                src="/hero.png"
                alt="Hero Illustration"
                fill
                className="object-contain"
                priority
              />
            </div>
          </div>
        </section>

        <AboutUs />

        {/* Our Work */}
        <section className="py-20 px-6">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Our Work</h2>
            <p className="text-gray-300 text-center mb-16 max-w-3xl mx-auto text-lg">
              Improving tracking and analytics through dynamic video and pose estimation tech integrated into real-world use cases.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10 text-center">
              {[
                { name: 'basketball', img: '/basketball.jpg' },
                { name: 'football', img: '/football.jpg' },
                { name: 'volleyball', img: '/volleyball.jpg' },
                { name: 'badminton', img: '/badminton.jpg' },
              ].map((sport) => (
                <div key={sport.name} className="bg-neutral-800 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-110">
                  <Image src={sport.img} alt={sport.name} width={200} height={200} className="mx-auto mb-8 rounded-xl" />
                  <p className="capitalize font-extrabold text-xl">{sport.name} Tracking</p>
                </div>
              ))}
            </div>
            <div className="mt-16">
              <iframe
                width="100%"
                height="500"
                src="https://www.youtube.com/embed/7chU45KjyK0"
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="rounded-lg shadow-lg"
              ></iframe>
            </div>
          </div>
        </section>

        {/* Services */}
        <section className="py-20 px-6 bg-neutral-900">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-5xl font-extrabold text-yellow-400 mb-12 text-center">Services Offered</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
              {[
                { title: 'Performance Analytics', img: '/performance.jpg' },
                { title: 'Tactical Insights', img: '/tactics.jpg' },
                { title: 'Injury Prevention & Health Monitoring', img: '/injury.jpg' },
              ].map((service) => (
                <div key={service.title} className="bg-neutral-800 p-8 rounded-3xl shadow-2xl hover:bg-neutral-700 transition transform hover:scale-110">
                  <Image src={service.img} alt={service.title} width={200} height={200} className="mx-auto mb-8 rounded-xl" />
                  <h3 className="text-2xl font-extrabold text-yellow-300 mb-4">{service.title}</h3>
                </div>
              ))}
            </div>
          </div>
        </section>

        <AwardsSection />
        <Testimonials />
        <WhyChooseUs />
        <BlogSection />
        <FAQSection />

        {/* Feedback Section */}
        <section className="py-20 px-6 bg-neutral-800">
          <div className="max-w-5xl mx-auto text-center">
            <h2 className="text-4xl font-extrabold text-yellow-400 mb-6">We Value Your Feedback</h2>
            <p className="text-lg text-gray-300 mb-8">Your feedback helps us improve. Please share your thoughts with us.</p>
            <Button
              onClick={toggleFeedbackForm}
              className="bg-yellow-400 text-black px-6 py-3 rounded-full hover:bg-yellow-500 transition"
            >
              Give Feedback
            </Button>

            {isFeedbackOpen && (
              <div className="fixed inset-0 flex justify-center items-center bg-black bg-opacity-30 z-20">
                <div className="bg-neutral-800 p-7 rounded-lg shadow-xl w-[500px] h-[500px] relative transform transition-all scale-95 hover:scale-100">
                  <button
                    onClick={toggleFeedbackForm}
                    className="absolute top-4 right-4 text-3xl text-neutral-300 hover:text-neutral-100 transition"
                  >
                    &times;
                  </button>
                  <h3 className="text-xl font-semibold text-neutral-100 mb-4 text-center">Feedback Form</h3>
                  <FeedbackForm />
                </div>
              </div>
            )}
          </div>
        </section>
      </main>

      <StarRating />
      <ChatBot />

      {/* Footer */}
      <footer className="bg-black text-yellow-400 pt-16 pb-10 px-6 mt-20 border-t border-white/10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12">
          <div>
            <div className="flex items-center mb-4 space-x-3">
              <Image src="/logo.png" alt="Orion Labs" width={50} height={50} className="rounded-full" />
              <p className="text-2xl font-extrabold">Orion Labs</p>
            </div>
            <p className="text-lg text-gray-400">
              Innovating sports tracking for the future of athletics. We create smart solutions that improve performance.
            </p>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-300">
              <li><Link href="/" className="hover:text-yellow-500">Home</Link></li>
              <li><Link href="/about" className="hover:text-yellow-500">About Us</Link></li>
              <li><Link href="/services" className="hover:text-yellow-500">Services</Link></li>
              <li><Link href="/work" className="hover:text-yellow-500">Our Work</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Contact Us</h4>
            <ul className="space-y-2 text-gray-300">
              <li><a href="mailto:info@orionlabs.com" className="hover:text-yellow-500">info@orionlabs.com</a></li>
              <li><a href="tel:+1234567890" className="hover:text-yellow-500">+1 (234) 567-890</a></li>
              <li><span className="hover:text-yellow-500">1234 Orion Blvd, New York</span></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-4">Follow Us</h4>
            <div className="flex space-x-6">
              <a href="#" className="hover:text-yellow-500"><FaTwitter size={24} /></a>
              <a href="#" className="hover:text-yellow-500"><FaLinkedin size={24} /></a>
              <a href="#" className="hover:text-yellow-500"><FaGithub size={24} /></a>
              <a href="#" className="hover:text-yellow-500"><FaFacebook size={24} /></a>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
