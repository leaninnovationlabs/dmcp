import { AuthProvider } from '@/contexts/AuthContext'
import { Toaster } from '@/components/ui/sonner'
import CloudStorageLayout from '@/components/CloudStorageLayout'

function App() {
  return (
    <AuthProvider>
      <CloudStorageLayout />
      <Toaster />
    </AuthProvider>
  )
}

export default App
