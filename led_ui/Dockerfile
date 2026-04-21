FROM node:20 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL}
ENV SKIP_ENV_VALIDATION=1
RUN npm run build

FROM node:20 AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
CMD ["npm", "start"]
