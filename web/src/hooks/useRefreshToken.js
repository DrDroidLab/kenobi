import useAuth from './useAuth';
import axios from 'axios';

const useRefreshToken = () => {
  const { setAuth, auth } = useAuth();

  const refresh = async () => {
    const response = await axios.post('/accounts/token/refresh/', {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true
    });
    setAuth({ ...auth, accessToken: response.data?.access });
    return response.data?.access;
  };

  return refresh;
};

export default useRefreshToken;
