# CS61Lab4

### Authors: Jacob Kingsley, Patrick Howard

### Notes:
- Before running the test files for the first time (or if you run one more than once), please clear the database by running the following `mongosh` queries
```
use blog
db.blogs.deleteMany({})
db.comments.deleteMany({})
db.posts.deleteMany({})
```

- Test with Terminal:

```
python blog.py < testfile1.in > grader.testfile1.out 2>&1
diff grader.testfile1.out testfile1.out
```

```
python blog.py < testfile2.in > grader.testfile2.out 2>&1
diff grader.testfile2.out testfile2.out
```