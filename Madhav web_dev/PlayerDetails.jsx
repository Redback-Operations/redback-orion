import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';

// Navbar component
const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  useEffect(() => {
    const closeMenu = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', closeMenu);

    return () => {
      document.removeEventListener('mousedown', closeMenu);
    };
  }, []);

  return (
    <nav className="bg-red-900 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-white text-xl font-semibold">Redback Operations</h1>
        <div className="relative" ref={menuRef}>
          <button className="text-white" onClick={toggleMenu}>
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M4 6h16M4 12h16m-7 6h7"
              ></path>
            </svg>
          </button>
          {menuOpen && (
            <div className="absolute right-0 mt-2 bg-black shadow-lg rounded-md">
              <button className="block px-4 py-2 text-red-800 hover:bg-gray-200 w-full text-left">
                Help
              </button>
              <button className="block px-4 py-2 text-red-800 hover:bg-gray-200 w-full text-left">
                LogOut
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

// Footer component
const Footer = () => {
  return (
    <footer className="bg-red-900 p-4 mt-auto">
      <div className="container mx-auto text-white text-center">
        <p>&copy; {new Date().getFullYear()} Redback Operations. All rights reserved.</p>
      </div>
    </footer>
  );
};

const PlayerDetails = () => {
  const [player, setPlayer] = useState({});
  const [loading, setLoading] = useState(false);
  const { id } = useParams();

  useEffect(() => {
    setLoading(true);
    axios
      .get(`http://localhost:5004/players/${id}`)
      .then((res) => {
        setPlayer(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.log(err);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <Navbar />
      <div className='p-4 bg-gradient-to-r from-purple-900 to-orange-500 min-h-screen flex justify-center items-center'>
        <div className='max-w-lg w-full'>
          <BackButton to="/players" className="ml-4" />
          <h1 className='text-3xl font-bold text-center text-black my-4 hover:text-white hover:underline'>Player Details</h1>
          {loading ? (
            <Spinner />
          ) : (
            <div className='flex flex-col border border-sky-400 rounded-lg p-4 bg-red-200 shadow-md'>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>ID:</span>
                <span className="hover:underline">{player._id}</span>
              </div>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>First Name:</span>
                <span className="hover:underline">{player.firstName}</span>
              </div>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>Last Name:</span>
                <span className="hover:underline">{player.lastName}</span>
              </div>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>Age:</span>
                <span className="hover:underline">{player.age}</span>
              </div>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>Team:</span>
                <span className="hover:underline">{player.team}</span>
              </div>
              <div className='my-4'>
                <span className='text-xl mr-4 text-black font-bold hover:underline'>Position:</span>
                <span className="hover:underline">{player.position}</span>
              </div>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default PlayerDetails;
