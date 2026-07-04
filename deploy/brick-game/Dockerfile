# Static nginx image serving the fixed brick-game example.
# (The Ornith-original lives in deploy/brick-breaker; this is the pi + GLM 5.2 fix.)
# Build context is the repo root so we can reach examples/.
FROM nginx:alpine
COPY examples/brick-game.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
