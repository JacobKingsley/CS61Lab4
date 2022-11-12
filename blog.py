### blog.py, a basic CLI for a Mongo-implemented Blog
### Authors: Jacob Kingsley and Patrick Howard

import pymongo
import sys
from shlex import split
import datetime
import re
from configparser import ConfigParser


# Connect to your MongoDB cluster:
try:
    parser = ConfigParser()
    parser.read("config.ini")
    username = parser.get('mongo', 'username')
    password = parser.get('mongo', 'password')

    #client = pymongo.MongoClient("mongodb+srv://{username}:{password}@cluster0.tj0ntky.mongodb.net/test")
    client = pymongo.MongoClient("mongodb+srv://JacobKingsley61:DylanBienstockXRE1@cluster0.tj0ntky.mongodb.net/test")
    print("Connection established.")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Connection failure:")
    print(err)

# Get a reference to the "blog" database:
db = client["blog"]

#format: post blogName userName title postBody tags timestamp
def post(blogName, userName, title, postBody, tags, timestamp):

    blogs = db["blogs"]
    blog = blogs.find_one({"blogName" : blogName})

    if not blog:
        blog = {"blogName": blogName,
                "postsWithin": []}
        blogs.insert_one(blog)
        print("new blog added to database")

    posts = db["posts"]

    #CHANGE TO PARAM timestamp DURING TESTING
    timeAcc = str(datetime.datetime.utcnow())
    permalink  = blogName +'.'+str(re.sub('[^0-9a-zA-Z]+', '_', title) + '_' + timeAcc)

    #build out tags list, splitting on space
    tagsArray = []
    if tags:
        tagsArray = tags.split(",")

    try:
        post = {"author": userName,
                "title" : title,
                "body": postBody,
                "tags": tagsArray,
                "timestamp": timeAcc,
                "permalink": permalink,
                "blogName" : blogName,
                "commentsWithin" : []}
        post_id = posts.insert_one(post).inserted_id
        print("post_id 1: {}".format(post_id))

    except Exception as e:
        print("Error trying to post: ", type(e), e)

    #now try to add link from blog to post using permalink

    try:
        blogs.update_one(
            {"blogName":blogName},
            {
                '$push': {
                    "postsWithin": permalink
                }
            }
        )

    except Exception as e:
        print("Error trying to link post to blog: ", type(e), e)

    print("post added")

#format: comment blogname permalink userName commentBody timestamp
def comment(blogname, permalink, userName, commentBody, timestamp):
    blogs = db["blogs"]
    blog = blogs.find_one({"blogName" : blogname})
    
    new_comment_timestamp = datetime.datetime.utcnow()
    comment = {
                    "blogName": blogname,
                    "permalink": new_comment_timestamp,
                    "userName": userName,
                    "comment" : commentBody,
                    "timestamp": new_comment_timestamp,
                    "commentsWithin" : []
                    }

    if blog: # 11/12 resolved - {need to figure out if this means a blog exists or just a mongo issue}
        posts = db["posts"]
        post = posts.find_one({"permalink": permalink})
        if post:
            comments = db['comments']
            try:
                comment_id = comments.insert_one(comment).inserted_id
                print("comment_id 1: {}".format(comment_id))

            except Exception as e:
                print("Error trying to comment: ", type(e), e)

            try:
                posts.update_one(
                    {"permalink":permalink},
                    {
                        '$push': {
                            "commentsWithin": new_comment_timestamp
                        }
                    }
                )

            except Exception as e:
                print("Error trying to link comment to post: ", type(e), e)
        else:
            comments = db["comments"]
            comment = comments.find_one({"permalink": permalink})
            if comment:
                try:
                    comment_id = comments.insert_one(comment).inserted_id
                    print("comment_id 1: {}".format(comment_id))

                except Exception as e:
                    print("Error trying to comment: ", type(e), e)

                try:
                    comments.update_one(
                        {"permalink":permalink},
                        {
                            '$push': {
                                "commentsWithin": new_comment_timestamp
                            }
                        }
                    )

                except Exception as e:
                    print("Error trying to link post to blog: ", type(e), e)
            else:
                print("invalid comment. The provided permalink is not a post or comment")
    else:
        print("invalid comment. the provided blog does not exist")

    print("comment added")


def delete(blogname, permalink, userName, timestamp):
    blogs = db["blogs"]
    blog = blogs.find_one({"blogName" : blogname})

    if blog:
        posts = db["posts"]
        post = posts.find_one({"permalink": permalink})
        if post:
            deleted_statement = "deleted by " + str(userName)
            try:
                posts.update_one(
                    {"permalink": permalink},
                    {
                        "$set" : {
                            "timestamp": datetime.datetime.utcnow(),
                            "body": deleted_statement
                        }
                    }
                )
                print("post deleted")

            except Exception as e:
                print("Error trying to delete post: ", type(e), e)
        else:
            comments = db["comments"]
            comment = comments.find_one({"permalink": permalink})
            if comment:
                deleted_statement = "deleted by " + str(userName)
                try:
                    comments.update_one(
                        {"permalink": permalink},
                        {
                            "$set" : {
                                "comment": deleted_statement,
                                "timestamp": datetime.datetime.utcnow()
                            }
                        }
                    )
                    print("comment deleted")

                except Exception as e:
                    print("Error trying to delete post: ", type(e), e)
            else:
                print("invalid delete. The provided permalink is not a post or comment")
    else:
        print("invalid delete. the provided blog does not exist")




def show(blogname):
    
    #prints a post and calls comment print on all nested comments
    #level keeps track of print indentation ("printdentation" - PH 11/12)
    def postPrint(permalink):
        posts = db["posts"]
        post = posts.find_one({"permalink" : permalink})
        level = 1
        if post:
            
            lprint("---------------- \n", level)
            lprint("Title: " + post['title'], level)
            lprint("Username: " + post['author'], level)
            if post['tags']:
                lprint("Tags: " + str(post['tags'])[1:-1], level) #interval on list-to-str removes brackets
            lprint("Timestamp: " + str(post['timestamp']), level)
            lprint("Permalink: " + post['permalink'], level)
            lprint("Contents: ", level) #New line per example and pop out a bit
            lprint(post['body'], level+1)

            comments = post['commentsWithin']
            for commentPerma in comments:
                commentPrint(commentPerma, level + 1)

            lprint("\n----------------", level)

        else:
            print("Post with permalink " + permalink + " not found.")
            return


    #level does tabbing
    def commentPrint(permalink, level):
        
        comments = db["comments"]
        comment = comments.find_one({"permalink" : permalink})
        
        if comment:
            print("\n")
            lprint("----------------", level)
            lprint("Username: " + comment['userName'], level)
            lprint("Permalink: " + str(comment['permalink']), level)
            lprint("Contents: ", level) #New line per example and pop out a bit
            lprint(comment['comment'], level+1)

            comments = comment['commentsWithin']
            for commentPerma in comments:
                commentPrint(commentPerma, level + 1)

            lprint("----------------", level)

        else:
            print("Comment with permalink " + permalink + " not found.")
            return

    #prints with levels for tabbing
    def lprint(str, level):
        printres = str
        for _ in range(level):
            printres = "    " + printres
        
        print(printres)

    #main driver
    blogs = db["blogs"]
    blog = blogs.find_one({"blogName" : blogname})

    if blog:
        
        allPosts = blog['postsWithin']
        print("\nIn blog " + blogname + ":")
        for arrayPerma in allPosts:
            postPrint(arrayPerma)
        
    else:
        print("invalid show command. Blog " + blogname + " does not exist.")
        return



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
        elif split(line)[0] == "quit":
            break
        else:
            read_line(line)


if __name__ == '__main__':
    read_input()