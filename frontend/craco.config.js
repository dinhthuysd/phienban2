// craco.config.js
const path = require("path");
require("dotenv").config();

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === "true",
  enableVisualEdits: process.env.REACT_APP_ENABLE_VISUAL_EDITS === "true",
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
};

// 🚫 Disable visual edits and health-check custom plugin loading if not available
let babelMetadataPlugin = null;
let setupDevServer = null;
let WebpackHealthPlugin = null;
let setupHealthEndpoints = null;
let healthPluginInstance = null;

// ✅ Only load visual edits plugin if file exists
try {
  if (config.enableVisualEdits) {
    babelMetadataPlugin = require("./plugins/visual-edits/babel-metadata-plugin");
    setupDevServer = require("./plugins/visual-edits/dev-server-setup");
  }
} catch (e) {
  console.warn("⚠️ Visual Edits plugin not found. Skipping...");
  config.enableVisualEdits = false;
}

// ✅ Only load health check plugin if file exists
try {
  if (config.enableHealthCheck) {
    WebpackHealthPlugin = require("./plugins/health-check/webpack-health-plugin");
    setupHealthEndpoints = require("./plugins/health-check/health-endpoints");
    healthPluginInstance = new WebpackHealthPlugin();
  }
} catch (e) {
  console.warn("⚠️ Health Check plugin not found. Skipping...");
  config.enableHealthCheck = false;
}

const webpackConfig = {
  webpack: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
    configure: (webpackConfig) => {
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        console.log("⚙️ Hot Reload disabled");
        webpackConfig.plugins = webpackConfig.plugins.filter(
          (plugin) => plugin.constructor.name !== "HotModuleReplacementPlugin"
        );
        webpackConfig.watch = false;
        webpackConfig.watchOptions = { ignored: /.*/ };
      } else {
        // Reduce watched directories for performance
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            "**/node_modules/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/coverage/**",
            "**/public/**",
          ],
        };
      }

      // Add health check plugin if available
      if (config.enableHealthCheck && healthPluginInstance) {
        webpackConfig.plugins.push(healthPluginInstance);
      }

      return webpackConfig;
    },
  },
};

// ✅ Add babel plugin safely
if (config.enableVisualEdits && babelMetadataPlugin) {
  webpackConfig.babel = {
    plugins: [babelMetadataPlugin],
  };
} else {
  webpackConfig.babel = { plugins: [] };
}

// ✅ Setup dev server safely
webpackConfig.devServer = (devServerConfig) => {
  // Apply visual edits setup if plugin is available
  if (config.enableVisualEdits && setupDevServer) {
    devServerConfig = setupDevServer(devServerConfig);
  }

  // Add health endpoints if available
  if (config.enableHealthCheck && setupHealthEndpoints && healthPluginInstance) {
    const originalSetupMiddlewares = devServerConfig.setupMiddlewares;
    devServerConfig.setupMiddlewares = (middlewares, devServer) => {
      if (originalSetupMiddlewares) {
        middlewares = originalSetupMiddlewares(middlewares, devServer);
      }
      setupHealthEndpoints(devServer, healthPluginInstance);
      return middlewares;
    };
  }

  return devServerConfig;
};

module.exports = webpackConfig;
