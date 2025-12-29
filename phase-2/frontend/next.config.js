const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Experimental features
  experimental: {
    // Externalize native modules that shouldn't be bundled
    serverComponentsExternalPackages: ['better-sqlite3'],
  },

  // Webpack configuration for path aliases
  webpack: (config, { isServer, dir }) => {
    // Use 'dir' provided by Next.js for reliable path resolution on Vercel
    const projectDir = dir || process.cwd();

    // Explicit path alias resolution
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.join(projectDir, 'src'),
    };

    // Ensure proper module resolution
    config.resolve.modules = [
      path.join(projectDir, 'src'),
      path.join(projectDir, 'node_modules'),
      'node_modules',
    ];

    // Externalize native modules completely
    if (isServer) {
      config.externals = config.externals || [];
      config.externals.push('better-sqlite3');
    }

    // Exclude native modules from client-side bundling
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        crypto: false,
        os: false,
        stream: false,
        buffer: false,
      };

      // Ignore better-sqlite3 on client side
      config.resolve.alias['better-sqlite3'] = false;
    }

    return config;
  },

  // Performance optimizations for Lighthouse
  poweredByHeader: false,

  // Compress responses
  compress: true,

  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
  },

  // Experimental features for better performance
  // Note: optimizeCss requires 'critters' package, disabled for build compatibility
  // experimental: {
  //   optimizeCss: true,
  // },

  // Headers for better caching and security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
      {
        source: '/:all*(svg|jpg|jpeg|png|gif|ico|webp|avif)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/:all*(js|css)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
