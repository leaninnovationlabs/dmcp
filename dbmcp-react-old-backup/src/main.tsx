import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './components/sidebar.css'
import App from './App'
import '@fortawesome/fontawesome-svg-core/styles.css'
import { library } from '@fortawesome/fontawesome-svg-core'
import { 
  faHome, 
  faDatabase, 
  faTools, 
  faSignOutAlt, 
  faChevronLeft, 
  faBars, 
  faTimes,
  faLink,
  faShieldAlt,
  faBolt,
  faServer,
  faPlus,
  faExclamationTriangle,
  faRedo,
  faPlug,
  faUser,
  faSpinner,
  faPlay,
  faTrash,
  faSave,
  faArrowLeft,
  faCog,
  faCheckCircle,
  faDownload
} from '@fortawesome/free-solid-svg-icons'

// Add icons to library
library.add(
  faHome, 
  faDatabase, 
  faTools, 
  faSignOutAlt, 
  faChevronLeft, 
  faBars, 
  faTimes,
  faLink,
  faShieldAlt,
  faBolt,
  faServer,
  faPlus,
  faExclamationTriangle,
  faRedo,
  faPlug,
  faUser,
  faSpinner,
  faPlay,
  faTrash,
  faSave,
  faArrowLeft,
  faCog,
  faCheckCircle,
  faDownload
)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
