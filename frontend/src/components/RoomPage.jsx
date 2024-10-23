import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosInstance from '../apis/axiosInstance';

function RoomPage() {
    const { roomId } = useParams();
    const [roomDetails, setRoomDetails] = useState(null);
    const canvasRef = useRef(null);
    const [ctx, setCtx] = useState(null);
    const socketRef = useRef(null);
    const prevCoordsRef = useRef({ prevX: 0, prevY: 0 });
    const navigate = useNavigate();

    const getUserEmailFromToken = () => {
        const token = localStorage.getItem('access_token');
        if (!token) return null;

        const accessToken = token;
        const payload = JSON.parse(atob(accessToken.split('.')[1]));
        return payload.email;
    };

    const currentUser = getUserEmailFromToken();

    useEffect(() => {
        // 방 정보 및 세션 생성
        const initializeRoom = async () => {
            try {
                // 방 정보 가져오기
                const roomResponse = await axiosInstance.get(`/rooms/${roomId}`);
                setRoomDetails(roomResponse.data);

                // 세션 생성하기
                await axiosInstance.post(`/rooms/session/${roomId}`);
            } catch (error) {
                console.error('Error initializing room:', error.response?.data?.detail);
            }
        };
        initializeRoom();
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
        if (!ctx || !roomDetails) return;

        const ws = new WebSocket(`ws://localhost:8000/ws/rooms/${roomId}`);
        socketRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connection opened');
        };

        // WebSocket 메시지 수신 처리
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'draw') {
                const { x, y, prevX, prevY } = data;
                ctx.beginPath();
                ctx.moveTo(prevX, prevY);
                ctx.lineTo(x, y);
                ctx.stroke();
            }
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed');
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        // 컴포넌트 언마운트 시 WebSocket 연결 해제
        return () => {
            ws.close();
        };
    }, [roomId, ctx, roomDetails]);

    const handleMouseMove = (event) => {
        if (event.buttons !== 1 || !ctx) return; // 마우스 왼쪽 버튼이 눌려있지 않으면 무시

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const { prevX, prevY } = prevCoordsRef.current;

        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(x, y);
        ctx.stroke();

        // WebSocket을 통해 그림 데이터 전송
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(
                JSON.stringify({ type: 'draw', x, y, prevX, prevY })
            );
        }

        // 이전 좌표 저장
        prevCoordsRef.current.prevX = x;
        prevCoordsRef.current.prevY = y;
    };

    const handleMouseDown = (event) => {
        if (!ctx) return; // ctx가 null인지 확인

        const rect = canvasRef.current.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        // 이전 좌표 초기화
        prevCoordsRef.current.prevX = x;
        prevCoordsRef.current.prevY = y;
    };

    const handleDeleteRoom = async () => {
        try {
            await axiosInstance.delete(`/rooms/${roomId}`);
            navigate('/');  // 방을 삭제한 후 메인 페이지로 이동
        } catch (error) {
            console.error('Error deleting room:', error.response?.data?.detail);
        }
    };

    const handleQuitRoom = async () => {
        try {
            await axiosInstance.delete(`/rooms/${roomId}/players`);
            navigate('/');  // 방을 나간 후 메인 페이지로 이동
        } catch (error) {
            console.error('Error quitting room:', error.response?.data?.detail);
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

            <button onClick={handleQuitRoom}>Quit Room</button>

            <div className="canvas-container">
                <div className="drawing-box">
                    <canvas
                        ref={canvasRef}
                        width={800}
                        height={600}
                        onMouseDown={handleMouseDown}
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
