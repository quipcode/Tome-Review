# import requests
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "t6ETyfTGMNkdQVBZlSg", "isbns": "9781632168146"})
# print(res.json())

import hashlib

p = input("Enter the password >>")      
hashpass = hashlib.md5(p.encode('utf8')).hexdigest()
print(hashpass)