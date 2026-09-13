FROM node:18-alpine

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Environment variables
ENV NODE_ENV=production
ENV BACKEND_URL=http://backend:8000

# Build the Next.js application
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
