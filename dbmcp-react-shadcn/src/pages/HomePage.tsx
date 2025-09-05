import HomeModule from '@/modules/home';

export default function HomePage() {
  return <HomeModule onModuleChange={() => {}} sidebarCollapsed={false} onToggleSidebar={() => {}} />;
}
