import { LoginModule } from '@/modules/auth';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    navigate('/');
  };

  return <LoginModule onLoginSuccess={handleLoginSuccess} />;
}
