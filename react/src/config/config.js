export const BASE_URL = process.env.REACT_APP_BASE_URL
export const API_URL = process.env.REACT_APP_API_URL
export const NODE_ENV = process.env.REACT_APP_NODE_ENV
export const wsProtocol = NODE_ENV === 'production' ? 'wss' : 'ws';