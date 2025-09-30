.PHONY: update

update:
	bundle lock --add-platform x86_64-linux
	git add .
	git commit -m "update"
	git push

local:
	npx -y @devcontainers/cli@latest up --workspace-folder /Users/CiCi/Project/ccsnow127.github.io