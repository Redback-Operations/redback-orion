import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Spinner from '../components/Spinner';
import Cursor from '../components/Cursor';
import { Link } from 'react-router-dom';
import { AiOutlineEdit } from 'react-icons/ai';
import { BsInfoCircle } from 'react-icons/bs';
import { MdOutlineAddBox, MdOutlineDelete } from 'react-icons/md';
import { RiPlayFill } from 'react-icons/ri';

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
  );
};

export default ListPlayers;
