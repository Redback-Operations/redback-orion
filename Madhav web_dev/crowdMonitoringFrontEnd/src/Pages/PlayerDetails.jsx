import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import BackButton from '../components/BackButton';
import Spinner from '../components/Spinner';

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
    );
};

export default PlayerDetails;
