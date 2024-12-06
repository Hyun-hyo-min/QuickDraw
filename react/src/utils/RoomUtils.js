export function setCurrentRoomId(roomId) {
    localStorage.setItem("currentRoomId", roomId);
}

export function getCurrentRoomId() {
    return localStorage.getItem("currentRoomId");
}

export function clearCurrentRoomId() {
    localStorage.removeItem("currentRoomId");
}
