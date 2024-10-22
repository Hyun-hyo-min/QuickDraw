import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';

function RoomList() {
    const [rooms, setRooms] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                const response = await axiosInstance.get('/room');
                console.log('Fetched rooms:', response.data);
                setRooms(response.data);
            } catch (error) {
                console.error('Error fetching rooms:', error.response.data.detail);
            }
        };
        fetchRooms();
    }, []);

    const handleJoinRoom = async (roomId) => {
        try {
            await axiosInstance.post(`/room/join/${roomId}`);
            navigate(`/room/${roomId}`);
        } catch (error) {
            console.error('Error joining room:', error.response.data.detail);
        }
    };

    return (
        <div>
            <h2>Available Rooms</h2>
            <ul>
                {rooms.map(room => (
                    <li key={room.id}>
                        {room.id}-{room.name} : {room.current_players}/{room.max_players}
                        <button onClick={() => handleJoinRoom(room.id)}>Join Room</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default RoomList;
