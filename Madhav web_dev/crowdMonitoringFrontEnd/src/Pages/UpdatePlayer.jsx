import React, { useState, useEffect } from 'react';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';

const UpdatePlayer = () => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [age, setAge] = useState('');
  const [team, setTeam] = useState('');
  const [position, setPosition] = useState('');
  const [DOB, setDOB] = useState('');
  const [sport, setSport] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const {id} = useParams();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:5004/players/${id}`)
      .then((res) => {
        const { firstName, lastName, age, team, position, dateOfBirth, sport } = res.data;
        setFirstName(firstName);
        setLastName(lastName);
        setAge(age);
        setTeam(team);
        setPosition(position);
        setDOB(dateOfBirth);
        setSport(sport);
        setLoading(false);
      }).catch((e) => {
        setLoading(false);
        enqueueSnackbar('An error occurred. Please check console.', { variant: 'error' });
        console.log(e);
      });
  }, []);

  const handleUpdatePlayer = () => {
    const data = {
      firstName,
      lastName,
      age,
      team,
      position,
      dateOfBirth: DOB,
      sport,
    };
    setLoading(true);
    axios.put(`http://localhost:5004/players/${id}`, data)
      .then(() => {
        setLoading(false);
        enqueueSnackbar('Player Data Edited successfully', { variant: 'success' });
        navigate('/players');
      }).catch((e) => {
        setLoading(false);
        enqueueSnackbar('Error', { variant: 'error' });
        console.log(e);
      });
  };

  return (
    <div className="bg-gradient-to-r from-purple-900 to-orange-500 min-h-screen flex flex-col justify-center items-center">
      <BackButton to={`/players`} className="ml-4 mt-4" />
      <h1 className="text-3xl font-bold text-center mb-6 hover:text-red-500 transition-colors duration-300">
        Update Player Details
      </h1>
      <div className="max-w-lg w-full p-8 bg-red-300 rounded-lg shadow-lg">
        {loading ? <Spinner /> : ''}
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
              type="number"
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
            <label className="text-xl text-black font-bold">DOB</label>
            <input
              type="date"
              value={DOB}
              onChange={(e) => setDOB(e.target.value)}
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
          <button
            className="py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-300 self-center"
            onClick={handleUpdatePlayer}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default UpdatePlayer;
