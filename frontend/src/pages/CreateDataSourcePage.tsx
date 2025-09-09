import { useNavigate } from 'react-router-dom';
import CreateDataSourceForm from '@/modules/data-sources/CreateDataSourceForm';

export default function CreateDataSourcePage() {
  const navigate = useNavigate();

  const handleSave = async (dataSource: any) => {
    try {
      // This will be handled by the form component itself
      // The form component already has the API integration
      console.log('DataSource saved:', dataSource);
    } catch (error) {
      console.error('Error saving datasource:', error);
    }
  };

  const handleCancel = () => {
    navigate('/data-sources');
  };

  return (
    <div className="p-4">
      <CreateDataSourceForm
        onSave={handleSave}
        onCancel={handleCancel}
      />
    </div>
  );
}
