# blackboard_crawler
###Small app that grabs all pdf files from a specified Blackboard link

This should now work with most any course/degree scheme some slight changes would be needed as I cannot have access to all other courses to test.

Also for ease of use it would be nice if a GUI was added, I'll try and do this in the future after more features are added.

###Usage

```
python3 ./main.py [-u|-url] <AberLearn Module URL> [-h]
```
If no URL is specified, the crawler scans Blackboard for any and all available modules to download.

####Linux:

1. Download the contents of dist
2. In terminal locate the dist folder and cd into it
3. Run "./main"
4. Enter username and password

####Other OS's

1. From a command line/terminal  
2. pip install bs4
3. python main.py
