# Static nginx image serving the self-contained brick-breaker example.
# Build context is the repo root so we can reach examples/.
FROM nginx:alpine
COPY examples/brick-breaker.html /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
