#!/bin/bash

# Create necessary directories
echo "Creating directory structure..."
mkdir -p backend frontend/src frontend/public

# Install Python dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r ../requirements.txt

# Start the FastAPI backend server
echo "Starting backend server..."
uvicorn api:app --reload &

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd ../frontend
npm install

# Ensure proper TypeScript configuration
if [ ! -f "tsconfig.json" ]; then
    echo "Creating TypeScript configuration..."
    echo '{
        "compilerOptions": {
            "target": "es5",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": true,
            "skipLibCheck": true,
            "esModuleInterop": true,
            "allowSyntheticDefaultImports": true,
            "strict": true,
            "forceConsistentCasingInFileNames": true,
            "noFallthroughCasesInSwitch": true,
            "module": "esnext",
            "moduleResolution": "node",
            "resolveJsonModule": true,
            "isolatedModules": true,
            "noEmit": true,
            "jsx": "react-jsx"
        },
        "include": ["src"]
    }' > tsconfig.json
fi

# Create React environment declaration file
echo "/// <reference types=\"react-scripts\" />" > src/react-app-env.d.ts

# Start the React development server
echo "Starting frontend server..."
npm start 