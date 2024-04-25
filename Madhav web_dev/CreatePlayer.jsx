import React, { useState, useEffect, useRef } from 'react';
import BackButton from '../components/BackButton.jsx';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { FaBars } from 'react-icons/fa'; // Import the menu icon from FontAwesome

const CreatePlayer = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [age, setAge] = useState('');
  const [team, setTeam] = useState('');
  const [position, setPosition] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [sport, setSport] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  const handleSavePlayer = () => {
    setError(null);
    const data = {
      firstName,
      lastName,
      age,
      team,
      position,
      dateOfBirth,
      sport,
    };

    if (
      !firstName ||
      !lastName ||
      !age ||
      !team ||
      !position ||
      !dateOfBirth ||
      !sport
    ) {
      setError('Please enter all the fields.');
      return;
    }

    setLoading(true);
    axios
      .post('http://localhost:5004/players', data)
      .then((res) => {
        setLoading(false);
        navigate('/players');
      })
      .catch((err) => {
        setLoading(false);
        console.log(err);
        setError('An error occurred while saving the player.');
      });
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="bg-gradient-to-r from-purple-900 to-orange-500 min-h-screen flex flex-col justify-center items-center">
      <div className="w-full p-6 bg-black mb-4 flex items-center justify-between">
        <BackButton to={`/players`} className="ml-4 mb-4" />
        <h1 className="text-white text-2xl font-bold" style={{ color: '#FFA500' }}>Redback Operations</h1> {/* Redback Operations heading */}
        <div className="text-white mr-4">
          {/* Use the FaBars icon inside the button */}
          <button className="focus:outline-none" onClick={() => setShowMenu(!showMenu)}>
            <FaBars />
          </button>
          {showMenu && (
            <div ref={menuRef} className="absolute right-0 mt-2 bg-black rounded-lg shadow-lg">
              <a
                href="#"
                className="block px-4 py-2 text-red-800 hover:bg-gray-200"
              >
                Details
              </a>
              <a
                href="#"
                className="block px-4 py-2 text-red-800 hover:bg-gray-200"
              >
                Statistics
              </a>
            </div>
          )}
        </div>
      </div>
      <div className="max-w-lg w-full p-8 bg-red-300 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center text-black mb-6 hover:text-red-500 transition-colors duration-300">
          Create New Player
        </h1>
        {loading && <Spinner />}
        <div className="flex flex-col gap-4 p-4">
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">First Name</label>
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Last Name</label>
            <input
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Age</label>
            <input
              type="text"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Team</label>
            <input
              type="text"
              value={team}
              onChange={(e) => setTeam(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Position</label>
            <input
              type="text"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Date of Birth</label>
            <input
              type="date"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xl text-black font-bold">Sport</label>
            <input
              type="text"
              value={sport}
              onChange={(e) => setSport(e.target.value)}
              className="border-2 border-gray-500 rounded-md px-4 py-2"
            />
          </div>
        </div>
        {error && <p className="text-red-500 text-center">{error}</p>}
        <div className="flex justify-center mt-6">
          <button
            className="py-2 px-4 bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-900 transition duration-300"
            onClick={handleSavePlayer}
          >
            Save
          </button>
        </div>
      </div>
      <Footer /> {/* Include the Footer component */}
    </div>
  );
};

// Footer component
const Footer = () => {
  return (
    <footer className="bg-black p-4 mt-auto w-full">
      <div className="container mx-auto text-center">
        <p className="text-sm text-white">&copy; {new Date().getFullYear()} <span className="font-bold text-orange-500">Redback Operations</span>. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default CreatePlayer;
