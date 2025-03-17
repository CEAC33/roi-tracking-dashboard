#!/bin/sh

# Create env.js with runtime environment variables
cat > /usr/share/nginx/html/env.js << EOF
window.env = {
  REACT_APP_API_URL: '${REACT_APP_API_URL}'
};
EOF

# Execute the main container command
exec "$@" 