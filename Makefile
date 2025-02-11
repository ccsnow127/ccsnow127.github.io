.PHONY: update

update:
	bundle lock --add-platform x86_64-linux
	git add .
	git commit -m "update"
	git push

# make msg m="Your commit message here"
msg:
	git add .
	git commit -m "$(m)"
	git push

local:
	docker compose up --build