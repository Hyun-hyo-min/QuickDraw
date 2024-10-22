import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    withCredentials: true,
});

axiosInstance.interceptors.request.use(
    (config) => {
        const tokenData = localStorage.getItem('access_token');
        if (tokenData) {
            try {
                const parsedTokenData = JSON.parse(tokenData);
                const accessToken = parsedTokenData?.token?.access_token;
                
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
