### blog.py, a file to 
### Authors: Jacob Kingsley and Patrick Howard

import pymongo
import sys
from shlex import split

# Connect to your MongoDB cluster:
try:
    client = pymongo.MongoClient("mongodb+srv://JacobKingsley61:DylanBienstockXRE1@cluster0.tj0ntky.mongodb.net/test")
    print("Connection established.")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Connection failure:")
    print(err)


# Get a reference to the "blog" database:
db = client["blog"]


def post(blogName, userName, title, postBody, tags, timestamp):
    if not blogName: ### not done, check if exists
        blogs = db["blogs"]
        blog = {"blogName": blogName}
        blogs.insert_one(blog)
    


def comment(blogname, permalink, userName, commentBody, timestamp):
    pass


def delete(blogname, permalink, userName, timestamp):
    pass

def show(blogname):
    pass


def read_line(line):
    words = split(line)
    if words[0] == "post":
        if len(words) != 7:
            print("invalid post transaction")
        else:
            post(words[1], words[2], words[3], words[4], words[5], words[6])
    elif words[0] == "comment":
        if len(words) != 6:
            print("invalid comment transaction")
        else:
            comment(words[1], words[2], words[3], words[4], words[5])
    elif words[0] == "delete":
        if len(words) != 5:
            print("invalid delete transaction")
        else:
            delete(words[1], words[2], words[3], words[4])
    elif words[0] == "show":
        if len(words) != 2:
            print("invalid show transaction")
        else:
            show(words[1])
    else:
        print("invalid transation")


def read_input():
    for line in sys.stdin:
        if line == "\n":
            pass
        elif not line:
            pass
        else:
            read_line(line)


if __name__ == '__main__':
    read_input()