import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "DBMCP Server",
  description: "Database Backend Server with MCP Support - Connect AI assistants to your databases through natural language",
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
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ]
  }
})
