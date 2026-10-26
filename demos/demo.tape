Source demos/settings.tape
Output docs/demo.gif

Hide
Type `cd /home/jean/pocs/length-prefixed-insert-sqli`
Enter
Type `export PS1='lab $ '`
Enter
Type `alias show='python3 demos/show.py'`
Enter
Type "clear"
Enter
Sleep 200ms
Show

Sleep 400ms
Type "show length-gate"
Sleep 250ms
Enter
Wait+Screen /LENGTH_MISMATCH/
Sleep 2s

Type "clear"
Enter
Sleep 300ms

Type "show vulnerable"
Sleep 250ms
Enter
Wait+Screen /HTTP 500/
Sleep 2.5s

Hide
Type `LAB_MODE=safe docker compose up -d --force-recreate --no-deps --wait app`
Enter
Wait+Line@60s /lab \$/
Type "clear"
Enter
Sleep 200ms
Show

Sleep 400ms
Type "show safe"
Sleep 250ms
Enter
Wait+Screen /HTTP 201/
Sleep 2.5s
