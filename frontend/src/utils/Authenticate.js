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