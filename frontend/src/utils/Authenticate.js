export const getToken = () => {
	const myToken = JSON.parse(localStorage.getItem('access_token'));

	if (!myToken)
		return null;

	return myToken
}

export const Logout = () => {
	localStorage.removeItem('access_token');
	window.location.reload();
}

export const getUserEmail = () => {
	const token = localStorage.getItem('access_token');
	if (!token) return null;

	const accessToken = token;
	const payload = JSON.parse(atob(accessToken.split('.')[1]));
	return payload.email;
};