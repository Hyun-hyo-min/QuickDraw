import React, { useEffect, useState } from 'react';
import axiosInstance from '../apis/axiosInstance';
import { useParams } from 'react-router-dom';

function RoomPage() {
    const { roomId } = useParams();
    const [roomDetails, setRoomDetails] = useState(null);
    
    useEffect(() => {
        const fetchRoomDetails = async () => {
            try {
                const response = await axiosInstance.get(`/room/${roomId}`);
                setRoomDetails(response.data);
            } catch (error) {
                console.error('Error fetching room details:', error.response?.data?.detail);
            }
        };
        fetchRoomDetails();
    }, [roomId]);

    if (!roomDetails) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Room: {roomDetails.name}</h2>
            <div className="canvas-container">
                <div className="drawing-box">
                    <canvas id="drawingCanvas" width="400" height="400"></canvas>
                </div>
                
                <div className="players-container">
                    <div className="players-left">
                        {roomDetails.players.slice(0, 4).map((player, index) => (
                            <div key={index} className="player-name">{player}</div>
                        ))}
                    </div>
                    <div className="players-right">
                        {roomDetails.players.slice(4, 8).map((player, index) => (
                            <div key={index} className="player-name">{player}</div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RoomPage;
