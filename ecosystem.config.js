module.exports = {
  apps: [
    {
      name: "announcements",
      script: "python",
      args: "main_linux.py",
      watch: false, // Change to true if you want to restart on file changes
      autorestart: true,
      max_restarts: 5,
      restart_delay: 5000, // Delay restarts to prevent rapid loops
      error_file: "announcements-error.log", // Error logs
      out_file: "announcements-out.log", // Standard logs
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
