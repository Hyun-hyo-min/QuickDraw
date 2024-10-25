import { GoogleLogin } from '@react-oauth/google'
import { jwtDecode } from 'jwt-decode'
import axiosInstance from '../apis/axiosInstance';
import React from 'react'

export const GoogleLoginBtn = () => {
    const loginHandle = (response) => {
        const decode_token = jwtDecode(response.credential)

        const data = {
            email: decode_token.email,
            name: decode_token.family_name + decode_token.given_name,
        }

        axiosInstance.post("/users/login/", data,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
            .then(response => {
                localStorage.setItem('access_token', JSON.stringify(response.data.access_token));
                window.location.reload()
            })
            .catch(error => {
                console.log(error)
            })
    }
    return (
        <>
            <GoogleLogin
                onSuccess={loginHandle}
                onError={() => {
                    console.log("Login Failed");
                }}
                width='300px'
            />
        </>
    )
}

export default GoogleLoginBtn