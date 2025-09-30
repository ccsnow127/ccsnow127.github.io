.PHONY: update

update:
	bundle lock --add-platform x86_64-linux
	git add .
	git commit -m "update"
	git push

local:
	bundle exec jekyll serve