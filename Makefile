.PHONY: ngrok

ngrok:
	ngrok http --url=meetbot.ngrok.io 8765
