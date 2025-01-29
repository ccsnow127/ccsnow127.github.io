.PHONY: update

update:
	git add .
	git commit -m "update"
	git push

msg:
	git add .
	git commit -m "$(m)"
	git push