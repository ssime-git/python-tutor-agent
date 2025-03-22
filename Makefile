launch:
	./setup.sh

run:
	docker compose down -v; docker image prune -f; docker compose up --build -d

clean:
	docker compose down -v
	docker image prune -f
	docker volume prune -f