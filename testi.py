from flask import request

event = "ssst"
goal = "students"
goal2 = "sssss"
c=0
ev = [i for i in event]
print(ev)
for i in goal:
    for j in goal2:

    if i in ev:
        c +=1
if c>=3:
    print("da")
else:
    print("ne")

