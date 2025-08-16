import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "DBMCP Server",
  description: "Database Backend Server with MCP Support - Connect AI assistants to your databases through natural language",
  head: [
    ['link', { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css' }]
  ],
  ignoreDeadLinks: [
    // Ignore localhost links that are only available when server is running
    /^http:\/\/localhost:8000/,
    /^http:\/\/127\.0\.0\.1:8000/
  ],
  markdown: {
    // Improve syntax highlighting
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  },
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Introduction', link: '/introduction' },
      { text: 'Get Started', link: '/get-started' }
    ],

    sidebar: [
      {
        text: 'Getting Started',
        items: [
          { text: 'Introduction', link: '/introduction' },
          { text: 'Installation & Setup', link: '/get-started' }
        ]
      },
      {
        text: 'Configuration',
        items: [
          { text: 'Configure DataSources', link: '/configure-datasources' },
          { text: 'Create Tools', link: '/create-tools' }
        ]
      },
      {
        text: 'Integration',
        items: [
          { text: 'Connect MCP Clients', link: '/connect-mcp-clients' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/leaninnovationlabs/dbmcp' }
    ]
  }
})
