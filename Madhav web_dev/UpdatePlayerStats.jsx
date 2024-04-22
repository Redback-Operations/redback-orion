import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';
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
    <nav className="bg-red-900  p-4">
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
                New Statistics
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

const UpdatePlayerStats = () => {
  const [gamesPlayed, setGamesPlayed] = useState('');
  const [goalsScored, setGoalsScored] = useState('');
  const [assists, setAssists] = useState('');
  const [yellowCards, setYellowCards] = useState('');
  const [redCards, setRedCards] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { id } = useParams();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    setLoading(true);
    axios
      .get(`http://localhost:5004/players/${id}/statistics`)
      .then((res) => {
        setGamesPlayed(res.data.gamesPlayed);
        setGoalsScored(res.data.goalsScored);
        setAssists(res.data.assists);
        setYellowCards(res.data.yellowCards);
        setRedCards(res.data.redCards);
        setLoading(false);
      })
      .catch((e) => {
        setLoading(false);
        enqueueSnackbar('An error occurred. Please check console.', { variant: 'error' });
        console.log(e);
      });
  }, []);

  const handleUpdatePlayerStats = () => {
    const data = {
      gamesPlayed,
      goalsScored,
      assists,
      yellowCards,
      redCards,
    };
    setLoading(true);
    axios
      .put(`http://localhost:5004/players/${id}/statistics`, data)
      .then(() => {
        setLoading(false);
        enqueueSnackbar('Player data edited successfully', { variant: 'success' });
        navigate('/players');
      })
      .catch((e) => {
        setLoading(false);
        enqueueSnackbar('Error', { variant: 'error' });
        console.log(e);
      });
  };

  return (
    <div>
      <Navbar />
      <div className="bg-gradient-to-r from-purple-900 to-orange-500">
        {/* This is the container immediately following the Navbar */}
      </div>
      <div className="container mx-auto p-6 rounded-lg shadow-lg font-apple bg-gradient-to-r from-purple-900 to-orange-500">
        <BackButton />
        <h1 className="text-3xl font-bold text-center text-black hover:text-white mb-8 transition duration-300">Update Player Stats</h1>
        {loading ? <Spinner /> : null}
        <div className="max-w-md mx-auto rounded-lg shadow-md p-6 bg-gradient-to-r from-purple-900 to-orange-500">
          <div className="grid grid-cols-1 gap-4">
            <div className="flex flex-col">
              <label className="text-lg text-white font-bold mb-1">Games Played</label>
              <input
                type="number"
                value={gamesPlayed}
                onChange={(e) => setGamesPlayed(e.target.value)}
                className="input rounded-md border border-white hover:border-blue-900 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-lg text-white font-bold mb-1">Goals Scored</label>
              <input
                type="number"
                value={goalsScored}
                onChange={(e) => setGoalsScored(e.target.value)}
                className="input rounded-md border border-white hover:border-blue-900 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-lg text-white font-bold mb-1">Assists</label>
              <input
                type="number"
                value={assists}
                onChange={(e) => setAssists(e.target.value)}
                className="input rounded-md border border-white hover:border-blue-900 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-lg text-white font-bold mb-1">Yellow Card(s)</label>
              <input
                type="number"
                value={yellowCards}
                onChange={(e) => setYellowCards(e.target.value)}
                className="input rounded-md border border-white hover:border-blue-900 px-3 py-2 text-sm"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-lg text-white font-bold mb-1">Red Card(s)</label>
              <input
                type="number"
                value={redCards}
                onChange={(e) => setRedCards(e.target.value)}
                className="input rounded-md border border-white hover:border-blue-900 px-3 py-2 text-sm"
              />
            </div>
          </div>
        </div>
        <div className="flex justify-center mt-6">
          <button
            className="py-2 px-4 bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-900 hover:bg-red-500 hover:text-xl hover:font-semibold transition duration-300"
            onClick={handleUpdatePlayerStats}
          >
            Save
          </button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default UpdatePlayerStats;

