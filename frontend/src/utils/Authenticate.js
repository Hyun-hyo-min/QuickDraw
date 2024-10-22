export const getToken = () => {
	const myToken = JSON.parse(localStorage.getItem('access_token'));
    
	if (!myToken)
		return null;

	if (myToken.expire <= Date.now()){
		localStorage.removeItem('access_token')
		return null;
	}
	return myToken.token
}

export const Logout = () => {
	localStorage.removeItem('access_token');
	window.location.reload();
}