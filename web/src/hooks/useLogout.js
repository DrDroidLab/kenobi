import useAuth from './useAuth';
import axios from 'axios';

const useLogout = () => {
  const { setAuth } = useAuth();

  const logout = async () => {
    setAuth({});
    try {
      const response = await axios.post('/accounts/logout/', '', {
        withCredentials: true
      });
    } catch (err) {
      console.error(err);
    }
  };

  return logout;
};

export default useLogout;
