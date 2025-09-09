import { createContext, useContext, useState, ReactNode } from 'react';

interface SessionContextType {
  isSessionExpired: boolean;
  showSessionExpired: () => void;
  hideSessionExpired: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [isSessionExpired, setIsSessionExpired] = useState(false);

  const showSessionExpired = () => {
    setIsSessionExpired(true);
  };

  const hideSessionExpired = () => {
    setIsSessionExpired(false);
  };

  return (
    <SessionContext.Provider
      value={{
        isSessionExpired,
        showSessionExpired,
        hideSessionExpired,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}
