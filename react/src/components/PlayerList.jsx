function PlayerList({ players }) {
    return (
        <div className="players-container">
            <div className="players-left">
                {players.slice(0, 4).map((player, index) => (
                    <div key={player.id} className="player-name">
                        {player.user_id}
                    </div>
                ))}
            </div>
            <div className="players-right">
                {players.slice(4, 8).map((player, index) => (
                    <div key={player.id} className="player-name">
                        {player.user_id}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default PlayerList;
