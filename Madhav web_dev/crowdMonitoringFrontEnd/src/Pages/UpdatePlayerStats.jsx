import React, { useState, useEffect } from 'react';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';

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
    <div className="container mx-auto mt-10 p-6 bg-gradient-to-r from-purple-900 to-orange-500 rounded-lg shadow-lg font-apple">
      <BackButton />
      <h1 className="text-3xl font-bold text-center text-black hover:text-white mb-8 transition duration-300">Update Player Stats</h1>
      {loading ? <Spinner /> : null}
      <div className="max-w-md mx-auto bg-red-200 rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 gap-4">
          <div className="flex flex-col">
            <label className="text-lg text-black font-bold mb-1">Games Played</label>
            <input
              type="number"
              value={gamesPlayed}
              onChange={(e) => setGamesPlayed(e.target.value)}
              className="input rounded-md border border-blue-500 hover:border-blue-900 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-lg text-black font-bold mb-1">Goals Scored</label>
            <input
              type="number"
              value={goalsScored}
              onChange={(e) => setGoalsScored(e.target.value)}
              className="input rounded-md border border-blue-500 hover:border-blue-900 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-lg text-black font-bold mb-1">Assists</label>
            <input
              type="number"
              value={assists}
              onChange={(e) => setAssists(e.target.value)}
              className="input rounded-md border border-blue-500 hover:border-blue-900 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-lg text-black font-bold mb-1">Yellow Card(s)</label>
            <input
              type="number"
              value={yellowCards}
              onChange={(e) => setYellowCards(e.target.value)}
              className="input rounded-md border border-blue-500 hover:border-blue-900 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-lg text-black font-bold mb-1">Red Card(s)</label>
            <input
              type="number"
              value={redCards}
              onChange={(e) => setRedCards(e.target.value)}
              className="input rounded-md border border-blue-500 hover:border-blue-900 px-3 py-2 text-sm"
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
  );
};

export default UpdatePlayerStats;
