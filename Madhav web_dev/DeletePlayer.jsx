import React, { useState, useEffect, useRef } from 'react';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';

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
                Details
              </button>
              <button className="block px-4 py-2 text-red-800 hover:bg-gray-200 w-full text-left">
                Statistics
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
        <p className="text-sm">&copy; {new Date().getFullYear()} Redback Operations. All rights reserved.</p>
      </div>
    </footer>
  );
};

const DeletePlayer = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();

  const handleDeletePlayer = () => {
    setLoading(true);
    axios
      .delete(`http://localhost:5004/players/${id}`)
      .then(() => {
        setLoading(false);
        enqueueSnackbar('Player Deleted successfully', { variant: 'success' });
        navigate('/players');
      })
      .catch((error) => {
        setLoading(false);
        enqueueSnackbar('Error', { variant: 'error' });
        console.log(error);
      });
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <div className="bg-gradient-to-r from-purple-900 to-orange-500 flex-grow flex flex-col justify-center items-center">
        <div className="max-w-lg w-full p-8 bg-red-300 rounded-lg shadow-lg">
          <BackButton to={`/players`} className="mb-4" />
          <h1 className="text-3xl font-bold text-center text-black mb-4 hover:text-red-500 transition-colors duration-300">
            Delete Player
          </h1>
          {loading ? <Spinner /> : ''}
          <div className="flex flex-col items-center border-2 border-sky-400 rounded-xl p-8">
            <h3 className="text-2xl mb-4">Are you sure you want to delete this player?</h3>

            <button
              className="py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-300"
              onClick={handleDeletePlayer}
            >
              Yes, Delete it (:0)
            </button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DeletePlayer;
