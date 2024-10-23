import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';

function RoomPage() {
    const { roomId } = useParams();
    const [roomDetails, setRoomDetails] = useState(null);
    const canvasRef = useRef(null);
    const [ctx, setCtx] = useState(null);
    const [socket, setSocket] = useState(null);
    const navigate = useNavigate();

    const getUserEmailFromToken = () => {
        const token = localStorage.getItem('access_token');
        if (!token) return null;

        const parsedToken = JSON.parse(token);
        const accessToken = parsedToken?.token?.access_token;
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        return payload.email;
    };

    const currentUser = getUserEmailFromToken();

    useEffect(() => {
        // 방 정보 가져오기
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

    useEffect(() => {
        if (canvasRef.current) {
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d');
            setCtx(context);
        }
    }, []);

    useEffect(() => {
        // WebSocket 연결 설정
        if (!ctx) return;

        const ws = new WebSocket(`ws://localhost:8000/ws/room/${roomId}`);
        setSocket(ws);

        // WebSocket 메시지 수신 처리
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'draw') {
                const { x, y } = data;
                ctx.beginPath();
                ctx.moveTo(data.prevX, data.prevY);
                ctx.lineTo(x, y);
                ctx.stroke();
            }
        };

        // WebSocket 연결 해제 처리
        return () => {
            ws.close();
        };
    }, [roomId, ctx]);

    const handleMouseMove = (event) => {
        if (event.buttons !== 1 || !ctx) return; // 마우스 왼쪽 버튼이 눌려있지 않으면 무시

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ctx.lineTo(x, y);
        ctx.stroke();

        // WebSocket을 통해 그림 데이터 전송
        if (socket) {
            socket.send(
                JSON.stringify({ type: 'draw', x, y, prevX: ctx.prevX, prevY: ctx.prevY })
            );
        }

        // 이전 좌표 저장
        ctx.prevX = x;
        ctx.prevY = y;
    };

    const handleDeleteRoom = async () => {
        try {
            await axiosInstance.delete(`/room/${roomId}`);
            navigate('/');  // 방을 삭제한 후 메인 페이지로 이동
        } catch (error) {
            console.error('Error deleting room:', error.response?.data?.detail);
        }
    };

    if (!roomDetails) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h2>Room: {roomDetails.room_name}</h2>

            {/* 현재 유저가 호스트일 경우에만 방 삭제 버튼을 표시 */}
            {currentUser === roomDetails.host && (
                <button onClick={handleDeleteRoom}>Delete Room</button>
            )}

            <div className="canvas-container">
                <div className="drawing-box">
                    <canvas
                        ref={canvasRef}
                        width={800}
                        height={600}
                        onMouseMove={handleMouseMove}
                        style={{ border: '1px solid black' }}
                    />
                </div>

                <div className="players-container">
                    <div className="players-left">
                        {roomDetails.players.slice(0, 4).map((player, index) => (
                            <div key={index} className="player-name">
                                {player}
                            </div>
                        ))}
                    </div>
                    <div className="players-right">
                        {roomDetails.players.slice(4, 8).map((player, index) => (
                            <div key={index} className="player-name">
                                {player}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RoomPage;
