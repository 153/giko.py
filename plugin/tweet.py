from mastodon import Mastodon
instance_url = "https://poa.st"

def cmd(author, msg):
    if msg.startswith("!tweet"):
        msg = msg[7:]
        mastodon.toot(msg)
        return(["It has been posted. https://poa.st/@gikobot"])

def setup():
    Mastodon.create_app(
        "gikobot",
        api_base_url = instance_url,
        to_file = "client.secret"
    )
    
def login():
    mastodon.log_in(
        "user",
        "password",
        to_file = "user.secret"
    )

if __name__ == "__main__":
    setup()
    mastodon = Mastodon(
        client_id = "client.secret",
        api_base_url = instance_url
        )
    login()

else:
    mastodon = Mastodon(
    client_id = "./data/client.secret",
    access_token = "./data/user.secret",
    api_base_url = instance_url
)

print("Tweet plugin loaded")
