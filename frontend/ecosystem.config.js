module.exports = {
  apps: [{
    name: 'nuxt-app',
    port: '3000',
    exec_mode: 'cluster',
    instances: 2,
    script: './.output/server/index.mjs',
    env: {
      NODE_ENV: 'production',
      NUXT_PUBLIC_API_BASE: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000',
      PORT: process.env.PORT || '3000'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_memory_restart: '1G',
    exp_backoff_restart_delay: 100,
    autorestart: true
  }]
}