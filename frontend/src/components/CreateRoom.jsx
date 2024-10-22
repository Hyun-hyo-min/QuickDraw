import React, { useState } from 'react';
import axiosInstance from '../apis/axiosInstance';

function CreateRoom() {
    const [roomName, setRoomName] = useState('');

    const handleCreateRoom = async (e) => {
        e.preventDefault();

        try {
            const response = await axiosInstance.post('/room', {
                room_name: roomName
            });
            alert('Room created: ' + response.data.room_id);
        } catch (error) {
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
