import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Database,
  Wrench,
  Shield,
  Zap,
  Link,
  Server,
  ChevronRight,
} from "lucide-react";

interface HomeModuleProps {
  onModuleChange?: () => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const HomeModule = ({
  onModuleChange: _onModuleChange,
  sidebarCollapsed: _sidebarCollapsed,
  onToggleSidebar: _onToggleSidebar,
}: HomeModuleProps) => {
  const navigate = useNavigate();

  const handleTryNow = () => {
    navigate("/data-sources");
  };

  const handleDatasourceClick = () => {
    navigate("/data-sources");
  };

  const handleToolsClick = () => {
    navigate("/tools");
  };

  return (
    <div className="overflow-auto bg-background">
      {/* Hero Section */}
      <div className="bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row lg:items-stretch">
            {/* Text Content */}
            <div className="flex-1 lg:pr-8 flex items-center p-20">
              <div className="text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-bold text-foreground sm:text-5xl md:text-6xl">
                  <span className="block xl:inline">Data</span>
                  <span className="block xl:inline xl:ml-2">MCP</span>
                </h1>
                <p className="mt-6 text-lg text-muted-foreground sm:mt-8 sm:text-xl sm:max-w-xl sm:mx-auto md:mt-8 md:text-xl lg:mx-0">
                  Securely connect to your data sources, create powerful tools,
                  and execute queries across multiple database types with our
                  intuitive interface.
                </p>
                <div className="mt-8 sm:mt-10 sm:flex sm:justify-center lg:justify-start gap-4">
                  <Button
                    onClick={handleTryNow}
                    className="bg-primary hover:bg-primary/90 text-primary-foreground border border-primary transition-all duration-200 hover:-translate-y-0.5 inline-flex items-center gap-2"
                  >
                    Try now
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Image Content */}
            {/* <div className="flex-1 lg:max-w-lg">
                <div className="h-80 w-full bg-[#FEBF23]/10 border-2 border-[#FEBF23] flex items-center justify-center rounded-lg" style={{margin: '25px 0'}}>
                  <div className="text-black text-center">
                    <div className="text-6xl mb-4">
                      <Database className="w-16 h-16 mx-auto" />
                    </div>
                    <h3 className="text-2xl font-semibold mb-2">Multiple Database Support</h3>
                    <p className="text-lg opacity-90">PostgreSQL • MySQL • SQLite</p>
                  </div>
                </div>
              </div> */}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-muted/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <Badge
              variant="secondary"
              className="text-base font-medium tracking-wide uppercase mb-2"
            >
              Features
            </Badge>
            <h2 className="mt-2 text-3xl leading-8 font-bold tracking-tight text-foreground sm:text-4xl">
              Everything you need to manage databases
            </h2>
            <p className="mt-4 max-w-2xl text-lg text-muted-foreground lg:mx-auto">
              DMCP provides a comprehensive suite of tools for database
              management and query execution.
            </p>
          </div>

          <div className="mt-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Database Connections Card */}
              <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center">
                      <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-primary text-primary-foreground mr-4">
                        <Link className="w-6 h-6" />
                      </div>
                      <div>
                        <CardTitle>Database Connections</CardTitle>
                        <CardDescription>
                          Connect to multiple database types
                        </CardDescription>
                      </div>
                    </div>
                    <Button
                      variant="link"
                      onClick={handleDatasourceClick}
                      className="text-primary underline font-medium hover:text-primary/80 p-0 h-auto"
                    >
                      Try now
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                        <Database className="text-primary-foreground text-sm" />
                      </div>
                      <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                        <Server className="text-primary-foreground text-sm" />
                      </div>
                      <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
                        <Database className="text-primary-foreground text-sm" />
                      </div>
                    </div>
                  </div>
                  <p className="text-muted-foreground">
                    Connect to PostgreSQL, MySQL, and SQLite databases with
                    secure encrypted password storage.
                  </p>
                </CardContent>
              </Card>

              {/* Query Tools Card */}
              <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center">
                      <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-primary text-primary-foreground mr-4">
                        <Wrench className="w-6 h-6" />
                      </div>
                      <div>
                        <CardTitle>Query Tools</CardTitle>
                        <CardDescription>
                          Create powerful database tools
                        </CardDescription>
                      </div>
                    </div>
                    <Button
                      variant="link"
                      onClick={handleToolsClick}
                      className="text-primary underline font-medium hover:text-primary/80 p-0 h-auto"
                    >
                      Try Now
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 mb-4">
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-primary rounded-full"></div>
                        <span className="text-sm text-muted-foreground">
                          Parameterized queries
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-primary rounded-full"></div>
                        <span className="text-sm text-muted-foreground">
                          Template support
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-primary rounded-full"></div>
                        <span className="text-sm text-muted-foreground">
                          Reusable components
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-muted-foreground">
                    Create reusable query tools with parameters and templates
                    for efficient database operations.
                  </p>
                </CardContent>
              </Card>

              {/* Security Card */}
              <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <CardHeader>
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-primary text-primary-foreground mr-4">
                      <Shield className="w-6 h-6" />
                    </div>
                    <div>
                      <CardTitle>Secure & Encrypted</CardTitle>
                      <CardDescription>
                        Enterprise-grade security
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 mb-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">
                        Encryption
                      </span>
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                      </div>
                    </div>
                  </div>
                  <p className="text-muted-foreground">
                    All sensitive data including passwords are encrypted at rest
                    using industry-standard encryption.
                  </p>
                </CardContent>
              </Card>

              {/* Performance Card */}
              <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <CardHeader>
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-primary text-primary-foreground mr-4">
                      <Zap className="w-6 h-6" />
                    </div>
                    <div>
                      <CardTitle>Fast & Responsive</CardTitle>
                      <CardDescription>
                        Modern async architecture
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="bg-muted rounded-lg p-4 mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-2 bg-muted-foreground/20 rounded-full overflow-hidden">
                        <div className="w-12 h-2 bg-primary rounded-full"></div>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        Performance
                      </span>
                    </div>
                  </div>
                  <p className="text-muted-foreground">
                    Modern async architecture ensures fast query execution and
                    responsive user interface.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-muted/50">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:py-20 lg:px-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl mb-4">
            <span className="block">Ready to get started?</span>
            <span className="block text-muted-foreground">
              Use the buttons above to begin managing your databases today.
            </span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Start by adding a data source to connect to your database, then
            create powerful tools to execute queries and manage your data
            efficiently.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomeModule;
