import axios from 'axios';
import { Logout } from '../utils/Authenticate';

const axiosInstance = axios.create({
    baseURL: `/api/v1`,
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const accessToken = JSON.parse(token);

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

axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        if (error.response && error.response.status === 401) {
            Logout();
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);


export default axiosInstance;
