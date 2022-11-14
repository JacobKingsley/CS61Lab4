# CS61Lab4

### Authors: Jacob Kingsley, Patrick Howard

### Notes:
- Before each file, please clear the database by running the following `mongosh` queries
```
use blog
db.blogs.deleteMany({})
db.comments.deleteMany({})
db.posts.deleteMany({})
```

- Test with Terminal (I use `zsh`, so syntax may slightly differ):

```
python blog.py < testfile1.in > testfile1.out
```

```
python blog.py < testfile2.in > testfile2.out
```