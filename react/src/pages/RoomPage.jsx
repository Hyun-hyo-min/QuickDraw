import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';
import { BASE_URL, API_URL, wsProtocol } from '../config/config';
import { getUserId } from '../utils/Authenticate';
import { getCurrentRoomId, setCurrentRoomId, clearCurrentRoomId } from '../utils/RoomUtils';
import { Canvas, RoomInfo, PlayerList, Chat } from '../components';

function RoomPage() {
    const { roomId } = useParams();
    const [roomDetails, setRoomDetails] = useState(null);
    const [chatMessages, setChatMessages] = useState([]);
    const [newMessage, setNewMessage] = useState("");
    const canvasRef = useRef(null);
    const [ctx, setCtx] = useState(null);
    const socketRef = useRef(null);
    const prevCoordsRef = useRef({ prevX: 0, prevY: 0 });
    const navigate = useNavigate();

    const currentUser = getUserId();

    useEffect(() => {
        const currentRoomId = getCurrentRoomId();
        if (currentRoomId && currentRoomId !== roomId) {
            navigate(`/rooms/${currentRoomId}`);
            return;
        }
        setCurrentRoomId(roomId);

        const initializeRoom = async () => {
            try {
                const roomResponse = await axiosInstance.get(`/room/${roomId}`);
                setRoomDetails(roomResponse.data);

                const drawingsResponse = await axiosInstance.get(`/draw/${roomId}`);
                const context = canvasRef.current.getContext("2d");

                if (context) {
                    setCtx(context);
                    drawingsResponse.data.forEach(({ x, y, prevX, prevY }) => {
                        context.beginPath();
                        context.moveTo(prevX, prevY);
                        context.lineTo(x, y);
                        context.stroke();
                    });
                }
            } catch (error) {
                navigate('/')
                console.error('Error initializing room:', error.response?.data?.detail);
            }
        };
        initializeRoom();
    }, [roomId]);

    useEffect(() => {
        if (roomDetails && canvasRef.current) {
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d');
            if (context) {
                setCtx(context);
            } else {
                console.error('Failed to get canvas context');
            }
        }
    }, [roomDetails]);

    useEffect(() => {
        if (!ctx || !roomDetails) return;

        const ws = new WebSocket(`${wsProtocol}://${BASE_URL}/ws/draw/${roomId}/user/${currentUser}`);
        socketRef.current = ws;

        ws.onopen = () => { };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'draw') {
                const { x, y, prevX, prevY } = data;
                ctx.beginPath();
                ctx.moveTo(prevX, prevY);
                ctx.lineTo(x, y);
                ctx.stroke();
            } else if (data.type === 'chat') {
                const message = `${data.email}: ${data.message}`;
                setChatMessages((prevMessages) => [...prevMessages, message]);

                setTimeout(() => {
                    setChatMessages((prevMessages) => prevMessages.slice(1));
                }, 10000);
            }
        };

        ws.onclose = () => { };

        return () => {
            ws.close();
        };
    }, [roomId, roomDetails, currentUser, ctx]);

    const handleMouseMove = (event) => {
        if (event.buttons !== 1 || !ctx) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const { prevX, prevY } = prevCoordsRef.current;

        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(x, y);
        ctx.stroke();

        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            const drawingData = { type: 'draw', x, y, prevX, prevY };
            socketRef.current.send(JSON.stringify(drawingData));
        }

        prevCoordsRef.current.prevX = x;
        prevCoordsRef.current.prevY = y;
    };

    const handleMouseDown = (event) => {
        if (!ctx) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        prevCoordsRef.current.prevX = x;
        prevCoordsRef.current.prevY = y;
    };

    const handleDeleteRoom = async () => {
        try {
            await axiosInstance.delete(`room/${roomId}`);
            navigate('/');
        } catch (error) {
            console.error('Error deleting room:', error.response?.data?.detail);
        }
    };

    const handleQuitRoom = async () => {
        try {
            await axiosInstance.delete(`room/${roomId}/players`);
            navigate('/');
        } catch (error) {
            console.error('Error quitting room:', error.response?.data?.detail);
        }
    };

    const handleSendMessage = () => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN && newMessage.trim()) {
            const chatData = {
                type: 'chat',
                user_id: currentUser,
                message: newMessage,
            };
            socketRef.current.send(JSON.stringify(chatData));
            setNewMessage("");
        }
    };

    if (!roomDetails) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <RoomInfo
                roomDetails={roomDetails}
                currentUser={currentUser}
                onDeleteRoom={() => {
                    clearCurrentRoomId();
                    handleDeleteRoom();
                }}
                onQuitRoom={() => {
                    clearCurrentRoomId();
                    handleQuitRoom();
                }}
            />
            <div className="room-container">
                <div className="main-container">
                    <Canvas
                        canvasRef={canvasRef}
                        handleMouseDown={handleMouseDown}
                        handleMouseMove={handleMouseMove}
                    />
                    <PlayerList players={roomDetails.players} />
                    <Chat
                        chatMessages={chatMessages}
                        newMessage={newMessage}
                        setNewMessage={setNewMessage}
                        onSendMessage={handleSendMessage}
                    />
                </div>
            </div>
        </div>
    );
}

export default RoomPage;
