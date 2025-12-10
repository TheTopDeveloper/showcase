# Frontend Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules
# Copy source code
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
# Ensure execute permissions and run build
RUN chmod -R +x node_modules/.bin && npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
# Copy standalone build (includes public if it exists)
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
# Ensure public directory exists (create empty if Next.js didn't include it)
RUN mkdir -p ./public && chown -R nextjs:nodejs ./public || true
USER nextjs
EXPOSE 8080
# Cloud Run sets PORT, but Next.js standalone uses PORT env var
ENV PORT=8080
ENV HOSTNAME="0.0.0.0"
# NEXT_PUBLIC_API_URL is baked into build, but set it here too for runtime
CMD ["sh", "-c", "node server.js"]
