function RoomInfo({ roomDetails, currentUser, onDeleteRoom, onQuitRoom }) {
    return (
        <div>
            <h2>Room: {roomDetails.room_name}</h2>
            {currentUser === roomDetails.host ? (
                <button onClick={onDeleteRoom}>Delete Room</button>
            ) : <></>}
            <button onClick={onQuitRoom}>Quit Room</button>
        </div>
    );
}

export default RoomInfo