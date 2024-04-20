while true; do
    rm -r irc.rizon.net
    ./ii -n GikoBot -i . -s irc.rizon.net &
    iipid="$!"
    sleep 5
    echo "/j #gikopoi" > ./irc.rizon.net/in
    wait "$iipid"
done
