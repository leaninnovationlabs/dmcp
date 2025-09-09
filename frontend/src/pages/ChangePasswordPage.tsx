import { ChangePasswordModule } from '@/modules/auth';
import { useNavigate } from 'react-router-dom';

export default function ChangePasswordPage() {
  const navigate = useNavigate();

  const handleSuccess = () => {
    navigate('/app');
  };

  const handleCancel = () => {
    navigate('/app');
  };

  return (
    <ChangePasswordModule 
      onSuccess={handleSuccess} 
      onCancel={handleCancel} 
    />
  );
}
