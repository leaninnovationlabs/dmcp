"use client"

import { useTheme } from "next-themes"
import { Toaster as Sonner, ToasterProps } from "sonner"

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme()

  return (
    <>
      <style jsx global>{`
        [data-sonner-toaster][data-theme] {
          --normal-bg: var(--popover);
          --normal-text: var(--popover-foreground);
          --normal-border: var(--border);
          --success-bg: #10b981;
          --success-text: #ffffff;
          --error-bg: #ef4444;
          --error-text: #ffffff;
        }
        
        [data-sonner-toaster] [data-sonner-toast] {
          transform: translateX(100%);
          animation: slideInFromRight 0.3s ease-out forwards;
        }
        
        @keyframes slideInFromRight {
          to {
            transform: translateX(0);
          }
        }
        
        [data-sonner-toast][data-type="success"] {
          background-color: #10b981 !important;
          color: #ffffff !important;
          border-color: #059669 !important;
        }
        
        [data-sonner-toast][data-type="error"] {
          background-color: #ef4444 !important;
          color: #ffffff !important;
          border-color: #dc2626 !important;
        }
      `}</style>
      <Sonner
        theme={theme as ToasterProps["theme"]}
        className="toaster group"
        position="top-right"
        richColors
        expand={true}
        {...props}
      />
    </>
  )
}

export { Toaster }
