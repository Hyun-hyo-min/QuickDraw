import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    withCredentials: true,
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const parsedToken = JSON.parse(token);
                const accessToken = parsedToken?.token?.access_token;
                
                if (accessToken) {
                    config.headers.Authorization = `Bearer ${accessToken}`;
                }
            } catch (error) {
                console.error("Failed to parse token data:", error);
            }
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default axiosInstance;
