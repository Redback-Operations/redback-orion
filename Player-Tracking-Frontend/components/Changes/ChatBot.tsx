'use client';
import { useState, useEffect, useRef } from 'react';
import { FaTimes, FaTwitter, FaLinkedin, FaGithub, FaFacebook } from 'react-icons/fa';
import { IoIosSend } from 'react-icons/io';
import Image from 'next/image';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showFooter, setShowFooter] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const toggleChat = () => {
    setIsOpen((prev) => !prev);
    if (!isOpen) {
      setMessages([{ sender: 'bot', text: getBotGreeting() }]);
    }
  };

  const handleSendMessage = async () => {
    const trimmedInput = userInput.trim();
    if (!trimmedInput) return;

    setMessages((prev) => [...prev, { sender: 'user', text: trimmedInput }]);
    setUserInput('');
    setIsTyping(true);

    setTimeout(() => {
      const lowerInput = trimmedInput.toLowerCase();

      let botReply = `You said: ${trimmedInput}`;
      if (lowerInput.includes('person')) {
        botReply = 'Would you like to connect with a real person?';
      } else if (lowerInput === 'yes') {
        setShowFooter(true);
        botReply = 'Connecting you with a real person...';
      }

      setMessages((prev) => [...prev, { sender: 'bot', text: botReply }]);
      setIsTyping(false);
    }, 1000);
  };

  const clearMessages = () => setMessages([]);

  const getBotGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning! How can I help you today?';
    if (hour < 18) return 'Good afternoon! How can I assist you?';
    return 'Good evening! How may I assist you?';
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <>
      <div className="fixed bottom-10 right-10 z-50">
        {isOpen ? (
          <div className="bg-gradient-to-b from-gray-800 to-gray-900 p-6 rounded-lg shadow-lg w-[370px] h-[450px] overflow-hidden transition-all">
            {/* Header */}
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl text-yellow-400 font-semibold">Chat with Us</h3>
              <button onClick={toggleChat} className="text-neutral-300 hover:text-neutral-100 transition-colors">
                <FaTimes size={20} />
              </button>
            </div>

            {/* Messages */}
            <div className="space-y-4 h-[290px] overflow-y-auto scrollbar-thin scrollbar-thumb-yellow-400 scrollbar-track-gray-800">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-xl max-w-[80%] ${
                    message.sender === 'user'
                      ? 'bg-yellow-400 text-black ml-auto'
                      : 'bg-neutral-600 text-white'
                  }`}
                  style={{
                    borderRadius: message.sender === 'user' ? '15px 15px 0px 15px' : '15px 15px 15px 0px',
                    boxShadow: '0 3px 8px rgba(0, 0, 0, 0.2)',
                  }}
                >
                  {message.text}
                </div>
              ))}
              {isTyping && <div className="p-3 text-gray-500 italic">...</div>}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="mt-4 flex items-center gap-2">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                className="flex-grow p-3 bg-neutral-700 text-white rounded-lg focus:outline-none transition-all"
                placeholder="Type a message..."
                disabled={isTyping}
              />
              <button
                onClick={handleSendMessage}
                className="ml-2 bg-yellow-400 text-black p-3 rounded-lg hover:bg-yellow-500 transition-colors"
                disabled={isTyping}
              >
                <IoIosSend size={20} />
              </button>
            </div>

            {/* Clear Button */}
            <button
              onClick={clearMessages}
              className="mt-4 bg-red-500 text-white p-3 rounded-lg w-full hover:bg-red-600 transition-colors"
            >
              Clear Chat
            </button>
          </div>
        ) : (
          <button
            onClick={toggleChat}
            className="bg-yellow-400 text-black p-4 rounded-full shadow-lg hover:bg-yellow-500 transition-colors"
          >
            Chat
          </button>
        )}
      </div>

      {/* Conditional Footer */}
      {showFooter && (
        <footer className="bg-black text-yellow-400 pt-16 pb-10 px-6 mt-20 border-t border-white/10">
          <div className="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-12">
            <div className="flex flex-col">
              <div className="flex items-center mb-4 space-x-3">
                <Image src="/logo.png" alt="Orion Labs" width={50} height={50} className="rounded-full" />
                <p className="text-2xl font-extrabold">Orion Labs</p>
              </div>
              <p className="text-lg text-gray-400 mb-6">
                Innovating sports tracking for the future of athletics. We create smart solutions that improve performance.
              </p>
            </div>

            <div className="flex flex-col">
              <h4 className="text-lg font-semibold text-yellow-400 mb-4">Quick Links</h4>
              <ul className="text-gray-300 space-y-2">
                <li><a href="#" className="hover:text-yellow-500">Home</a></li>
                <li><a href="#" className="hover:text-yellow-500">About Us</a></li>
                <li><a href="#" className="hover:text-yellow-500">Services</a></li>
                <li><a href="#" className="hover:text-yellow-500">Our Work</a></li>
              </ul>
            </div>

            <div className="flex flex-col">
              <h4 className="text-lg font-semibold text-yellow-400 mb-4">Contact Us</h4>
              <ul className="text-gray-300 space-y-2">
                <li><a href="mailto:info@orionlabs.com" className="hover:text-yellow-500">info@orionlabs.com</a></li>
                <li><a href="tel:+1234567890" className="hover:text-yellow-500">+1 (234) 567-890</a></li>
                <li><a href="#" className="hover:text-yellow-500">1234 Orion Blvd, New York</a></li>
              </ul>
            </div>

            <div className="flex flex-col">
              <h4 className="text-lg font-semibold text-yellow-400 mb-4">Follow Us</h4>
              <div className="flex space-x-6">
                <a href="#" className="text-gray-300 hover:text-yellow-500"><FaTwitter size={24} /></a>
                <a href="#" className="text-gray-300 hover:text-yellow-500"><FaLinkedin size={24} /></a>
                <a href="#" className="text-gray-300 hover:text-yellow-500"><FaGithub size={24} /></a>
                <a href="#" className="text-gray-300 hover:text-yellow-500"><FaFacebook size={24} /></a>
              </div>
            </div>
          </div>
        </footer>
      )}
    </>
  );
};

export default Chatbot;
