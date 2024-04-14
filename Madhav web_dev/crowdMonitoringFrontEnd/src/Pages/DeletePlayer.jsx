import React, { useState } from 'react';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';

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
    <div className="bg-gradient-to-r from-purple-900 to-orange-500 min-h-screen flex flex-col justify-center items-center">
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
  );
};

export default DeletePlayer;
