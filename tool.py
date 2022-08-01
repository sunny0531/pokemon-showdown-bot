import json
amount=input()
result={}
while True:
    a=input().lower()
    if a !="q":
        if not a.isspace():
            result[a]=float(amount)
    else:
        print(json.dumps(result)[1:-1])
        break