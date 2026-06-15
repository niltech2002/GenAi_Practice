num =int(input("enter num: "))
flag=1

if (num<=1):
    flag=0

for i in range(2,num):
    if(num%i==0):
        flag=0
        break

if(num>0 and flag==1):
    print(f"{num} is prime")
else:
    print(f"{num} is not prime")