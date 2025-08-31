---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "Data MCP"
  text: "Connect to any data source via query, API, or code"
  tagline: Connect AI assistants to your data
  image:
    src: /icons/logo.png
    width: 400
    alt: DMCP Logo
  actions:
    - theme: brand
      text: Introduction
      link: /introduction
    - theme: alt
      text: Get Started
      link: /get-started

features:
  - title: Multi-Data Source Support
    details: Connect to PostgreSQL, MySQL, Databricks, APIs, and more with unified interface
    icon: 🗄️
  - title: MCP Integration
    details: Expose data operations as tools for AI assistants using the Model Context Protocol
    icon: 🤖
  - title: Jinja Templating
    details: Dynamic queries with parameter support and conditional logic
    icon: 📝
  - title: Web Interface
    details: Intuitive UI for managing datasources, tools, and testing connections
    icon: 🌐
  - title: HTTP Request
    details: Build tools that can make HTTP requests to external APIs (coming soon)
    icon: 🔐
  - title: Easy Setup
    details: Simple installation with uv package manager and comprehensive documentation
    icon: ⚡

