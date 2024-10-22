import React, { useState, useEffect } from 'react';
import axiosInstance from '../apis/axiosInstance';

function RoomList() {
    const [rooms, setRooms] = useState([]);
    
    useEffect(() => {
        const fetchRooms = async () => {
            try {
                const response = await axiosInstance.get('/api/v1/rooms');
                setRooms(response.data);
            } catch (error) {
                console.error('Error fetching rooms:', error.response.data.detail);
            }
        };
        fetchRooms();
    }, []);

    const handleJoinRoom = async (roomId) => {
        try {
            const response = await axiosInstance.post(`/room/join/${roomId}`);
            alert(`Joined room: ${roomId}`);
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
                        {room.name} - {room.players.length}/{room.max_players} players
                        <button onClick={() => handleJoinRoom(room.id)}>Join Room</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default RoomList;
