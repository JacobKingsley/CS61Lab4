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
        blogs.insert_one({"blogName": blogName,
                "postsWithin": []})
        print("new blog added to database")

    posts = db["posts"]

    timeAcc = timestamp
    #Uncomment the following line to use real timestamps — using passed-in values for grader testing
    # timeAcc = str(datetime.datetime.utcnow())
    permalink  = blogName +'.'+str(re.sub('[^0-9a-zA-Z]+', '_', title) + '_' + timeAcc)

    # #build out tags list, splitting on space
    # tagsArray = []
    # if tags:
    #     tagsArray = tags.split(",")

    try:
        posts.insert_one({"author": userName,
                "title" : title,
                "body": postBody,
                "tags": tags,
                "timestamp": timeAcc,
                "permalink": permalink,
                "blogName" : blogName,
                "commentsWithin" : []})

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

    if blog: # 11/12 resolved - {need to figure out if this means a blog exists or just a mongo issue}
        posts = db["posts"]
        post = posts.find_one({"permalink": permalink})
        if post:
            comments = db['comments']
            try:
                
                permaFormat = timestamp
                #Uncomment the following line to use real timestamps — using passed-in values for grader testing
                #permaFormat = str(new_comment_timestamp)

                comments.insert_one({
                    "permalink": permaFormat,
                    "blogName": blogname,
                    "userName": userName,
                    "comment" : commentBody,
                    "timestamp": new_comment_timestamp,
                    "commentsWithin" : []
                    })

            except Exception as e:
                print("Error trying to comment: ", type(e), e)

            try:
                posts.update_one(
                    {"permalink":permalink},
                    {
                        '$push': {
                            "commentsWithin": permaFormat
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

                    permaFormat = timestamp
                    #Uncomment the following line to use real timestamps — using passed-in values for grader testing
                    #permaFormat = str(new_comment_timestamp)

                    comments.insert_one({
                    "permalink": permaFormat,
                    "blogName": blogname,
                    "userName": userName,
                    "comment" : commentBody,
                    "timestamp": new_comment_timestamp,
                    "commentsWithin" : []
                    })

                except Exception as e:
                    print("Error trying to comment: ", type(e), e)

                try:
                    comments.update_one(
                        {"permalink":permalink},
                        {
                            '$push': {
                                "commentsWithin": permaFormat
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

                timeFormat = timestamp
                #Uncomment the following line to use real timestamps — using passed-in values for grader testing
                #timeFormat = str(datetime.datetime.utcnow())

                posts.update_one(
                    {"permalink": permalink},
                    {
                        "$set" : {
                            "timestamp": timeFormat,
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

                    timeFormat = timestamp
                    #Uncomment the following line to use real timestamps — using passed-in values for grader testing
                    #timeFormat = str(datetime.datetime.utcnow())

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
            
            lprint("----------------", level)
            lprint("Title: " + post['title'], level)
            lprint("Username: " + post['author'], level)
            if post['tags']:
                # lprint("Tags: " + str(post['tags'])[1:-1], level) #interval on list-to-str removes brackets
                lprint("Tags: " + post['tags'], level)
            lprint("Timestamp: " + str(post['timestamp']), level)
            lprint("Permalink: " + post['permalink'], level)
            lprint("Contents: ", level) #New line per example and pop out a bit
            lprint(post['body'], level+1)

            comments = post['commentsWithin']
            for commentPerma in comments:
                commentPrint(commentPerma, level + 1)

            lprint("----------------", level)

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
            lprint("Permalink: " + comment['permalink'], level)
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
            print("\n")
        
    else:
        print("invalid show command. Blog " + blogname + " does not exist.")
        return


def find(blogName, searchString):
    def postPrint(post):
        level = 1
        if post:
            lprint("----------------", level)
            lprint("Title: " + post['title'], level)
            lprint("Username: " + post['author'], level)
            if post['tags']:
                # lprint("Tags: " + str(post['tags'])[1:-1], level) #interval on list-to-str removes brackets
                lprint("Tags: " + post['tags'], level)
            lprint("Timestamp: " + str(post['timestamp']), level)
            lprint("Permalink: " + post['permalink'], level)
            lprint("Contents: ", level) #New line per example and pop out a bit
            lprint(post['body'], level+1)

            lprint("----------------", level)
            print("\n")

    #prints with levels for tabbing
    def lprint(str, level):
        printres = str
        for _ in range(level):
            printres = "    " + printres
        
        print(printres)

    def commentPrint_noperm(comment):
        level = 1
        if comment:
            lprint("----------------", level)
            lprint("Username: " + comment['userName'], level)
            lprint("Permalink: " + comment['permalink'], level)
            lprint("Contents: ", level) #New line per example and pop out a bit
            lprint(comment['comment'], level+1)

            lprint("----------------", level)
            print("\n")

    search_regex = ".*" + searchString + ".*"

    print("Searching for " + str(searchString) + " in " + str(blogName) + ":")

    posts = db["posts"]
    posts_in_blog = posts.find({"blogName" : blogName, "$or": [{"body": {"$regex": search_regex}}, {"tags": {"$regex": search_regex}}]})
    for post in posts_in_blog:
        postPrint(post)

    comments = db['comments']
    comments_in_blog = comments.find({"blogName" : blogName, "comment": {"$regex" : search_regex}})
    for comment in comments_in_blog:
        commentPrint_noperm(comment)
    
    print("\n")



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
    elif words[0] == "find":
        if len(words) != 3:
            print("invalid find transaction")
        else:
            find(words[1], words[2])

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