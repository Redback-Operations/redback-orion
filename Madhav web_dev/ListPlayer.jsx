import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Spinner from '../components/Spinner';
import Cursor from '../components/Cursor';
import { Link } from 'react-router-dom';
import { AiOutlineEdit } from 'react-icons/ai';
import { BsInfoCircle } from 'react-icons/bs';
import { MdOutlineAddBox, MdOutlineDelete } from 'react-icons/md';
import { RiPlayFill } from 'react-icons/ri';

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
    <nav className="bg-purple-900 p-4">
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
                Statistics
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
    <footer className="bg-purple-900 p-4 mt-auto">
      <div className="container mx-auto text-white text-center">
        <p>&copy; {new Date().getFullYear()} Redback Operations. All rights reserved.</p>
      </div>
    </footer>
  );
};

const ListPlayers = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    axios
      .get('http://localhost:5004/players')
      .then((response) => {
        setPlayers(response.data.data);
        setLoading(false);
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <Navbar />
      <div className="bg-gradient-to-r from-purple-900 to-orange-500 min-h-screen flex justify-center items-center">
        <div className='p-4 w-full max-w-screen-lg'>
          <div className='flex justify-center items-center mb-8'>
            <h1 className='text-3xl font-semibold text-black hover:text-red-100 cursor-pointer font-san-francisco'>
              Player List
            </h1>
            <Link to='/player/create' className='ml-4'>
              <MdOutlineAddBox className='text--200 text-4xl' />
            </Link>
          </div>
          {loading ? (
            <Spinner />
          ) : (
            <div className="overflow-x-auto">
              <table className='w-full border-collapse rounded-lg overflow-hidden shadow-lg'>
                <thead>
                  <tr className="bg-red text-yellow">
                    <th className='border p-3 text-xl bg-yellow-100 text--800 rounded-tl-lg border-black'>
                      No
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Player Name
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Team
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Position
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Date of Birth
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Sport
                    </th>
                    <th className='border p-3 text-xl bg-yellow-100 text--800 border-black'>
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {players.map((player, index) => (
                    <tr
                      key={player._id}
                      className={`h-12 ${
                        index % 2 === 0 ? 'bg-green-300' : 'bg-green-200'
                      }`}
                    >
                      <td className='border p-3 text-center text-black border-black'>{index + 1}</td>
                      <td className='border p-3 text-yellow text-black border-black'>{`${player.firstName} ${player.lastName}`}</td>
                      <td className='border p-3 text-yellow text-black border-black'>{player.team}</td>
                      <td className='border p-3 text-yellow text-black border-black'>{player.position}</td>
                      <td className='border p-3 text-yellow text-black border-black'>{player.dateOfBirth}</td>
                      <td className='border p-3 text-yellow text-black border-black'>{player.sport}</td>
                      <td className='border p-3 text-center'>
                        <div className='flex justify-around gap-4'>
                          <Link
                            to={`/player/${player._id}`}
                            className='text-purple-600 hover:text-purple-800 transition duration-300'
                          >
                            <BsInfoCircle className='text-2xl' />
                          </Link>
                          <Link
                            to={`/player/update/${player._id}`}
                            className='text-yellow-600 hover:text-yellow-800 transition duration-300'
                          >
                            <AiOutlineEdit className='text-2xl' />
                          </Link>
                          <Link
                            to={`/player/delete/${player._id}`}
                            className='text-red-600 hover:text-red-800 transition duration-300'
                          >
                            <MdOutlineDelete className='text-2xl' />
                          </Link>
                          <Link
                            to={`/player/movements/${player._id}`}
                            className='text-green-600 hover:text-green-800 transition duration-300'
                          >
                            <RiPlayFill className='text-2xl' />
                          </Link>
                          <Link
                            to={`/player/update/stats/${player._id}`}
                            className='text-orange-600 hover:text-orange-800 transition duration-300'
                          >
                            <MdOutlineAddBox className='text-2xl' />
                          </Link>
                          <Cursor />
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default ListPlayers;
