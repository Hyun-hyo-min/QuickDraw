import { GoogleLogin } from '@react-oauth/google'
import axios from 'axios'
import { jwtDecode } from 'jwt-decode'
import React from 'react'

export const GoogleLoginBtn = () => {
    const loginHandle = (response) => {
        const decode_token = jwtDecode(response.credential)

        const data = {
            email: decode_token.email,
            name: decode_token.family_name + decode_token.given_name,
            exp: decode_token.exp
        }

        axios.post("http://localhost:8000/api/v1/user/login", data,
            {
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        )
            .then(response => {
                const accessToken = {
                    token: response.data,
                    expire: Date.now() + 60 * 60 * 1000
                };
                localStorage.setItem('access_token', JSON.stringify(accessToken));
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