export const getToken = () => {
	const myToken = JSON.parse(localStorage.getItem('token'));
    
	if (!myToken)
		return null;

	if (myToken.expire <= Date.now()){
		localStorage.removeItem('token')
		return null;
	}
	return myToken.token
}

export const Logout = () => {
	localStorage.removeItem('token');
	window.location.reload();
}