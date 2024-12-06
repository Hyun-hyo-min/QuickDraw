function Canvas({ canvasRef, handleMouseDown, handleMouseMove }) {
    return (
        <div className="canvas-container">
            <div className="drawing-box">
                <canvas
                    ref={canvasRef}
                    width={1400}
                    height={600}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    style={{ border: '1px solid black' }}
                />
            </div>
        </div>
    );
}

export default Canvas