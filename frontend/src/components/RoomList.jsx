import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';
import CreateRoom from './CreateRoom';

function RoomList() {
    const [rooms, setRooms] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const pageSize = 10;
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRooms = async () => {
            try {
                const response = await axiosInstance.get(`/rooms?page=${page}&page_size=${pageSize}`);
                setRooms(response.data.rooms || []);
                setTotalPages(response.data.total_pages);
            } catch (error) {
                console.error('Error fetching rooms:', error.response?.data?.detail || 'Unknown error');
            }
        };
        fetchRooms();
    }, [page]);

    const handleJoinRoom = async (roomId) => {
        try {
            await axiosInstance.post(`/rooms/${roomId}/players`);
            navigate(`/rooms/${roomId}`);
        } catch (error) {
            console.error('Error joining room:', error.response?.data?.detail || 'Unknown error');
        }
    };

    const handlePageChange = (newPage) => {
        setPage(newPage);
    };

    return (
        <div>
            <CreateRoom />
            <h2>Available Rooms</h2>
            <ul>
                {rooms.length > 0 ? (
                    rooms.map(room => (
                        <li key={room.id}>
                            {room.id} - {room.name} : {room.current_players}/{room.max_players}
                            <button onClick={() => handleJoinRoom(room.id)}>Join Room</button>
                        </li>
                    ))
                ) : (
                    <li>No rooms available</li>
                )}
            </ul>

            {/* 페이지네이션 버튼 */}
            <div>
                <button
                    onClick={() => handlePageChange(page - 1)}
                    disabled={page === 1}
                >
                    Previous
                </button>
                <span> Page {page} of {totalPages} </span>
                <button
                    onClick={() => handlePageChange(page + 1)}
                    disabled={page === totalPages}
                >
                    Next
                </button>
            </div>
        </div>
    );
}

export default RoomList;
