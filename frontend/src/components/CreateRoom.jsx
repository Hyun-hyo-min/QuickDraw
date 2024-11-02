import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';

function CreateRoom() {
    const [roomName, setRoomName] = useState('');
    const navigate = useNavigate();

    const handleCreateRoom = async (e) => {
        e.preventDefault();

        try {
            const response = await axiosInstance.post('/rooms', {
                room_name: roomName
            });
            const roomId = response.data.room_id;
            navigate(`/rooms/${roomId}`)
        } catch (error) {
            navigate(`/`)
            console.error('Error creating room:', error.response.data.detail);
        }
    };

    return (
        <div>
            <h2>Create Room</h2>
            <form onSubmit={handleCreateRoom}>
                <input 
                    type="text" 
                    placeholder="Room Name" 
                    value={roomName}
                    onChange={(e) => setRoomName(e.target.value)}
                    required
                />
                <button type="submit">Create Room</button>
            </form>
        </div>
    );
}

export default CreateRoom;
