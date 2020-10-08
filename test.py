import memcache

if __name__ == '__main__':
    cli = memcache.Client(["127.0.0.1:11211"], debug=True)
    cli.set("username", "hehe123", time=120)
    cli.set_multi({"username": "hehe123", "password": "12122"}, time=120)
    print(cli.get("username"))
    print(cli.get("password"))
