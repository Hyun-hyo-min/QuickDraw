import { GoogleLogin } from '@react-oauth/google'
import axiosInstance from '../apis/axiosInstance';
import React from 'react'

export const GoogleLoginBtn = () => {
    const loginHandle = (response) => {
        axiosInstance.post("users/login", { credential: response.credential }, {
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                localStorage.setItem('access_token', JSON.stringify(response.data.access_token));
                window.location.reload()
            })
            .catch(error => {
                console.log("Login Failed:", error)
            })
    }

    return (
        <GoogleLogin
            onSuccess={loginHandle}
            onError={() => console.log("Login Failed")}
            width='300px'
        />
    )
}

export default GoogleLoginBtn