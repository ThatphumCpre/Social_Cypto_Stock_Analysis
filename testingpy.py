import csv
fin_name = "stockdata.csv"
while True :
    with open(fin_name, 'a', newline='') as fin:
            writer = csv.writer(fin)
            prodID = input("")
            prodName = input("")
            print("h")
            while True  :
                print("i")
                try :
                    unitPrice =  float(input())
                except :
                    print("lusdsadl")
                else :
                    break
            while True :
                print("j")
                try :
                    qty = int(input())
                except :
                    print("lul")
                else :
                    break
            totalPrice = unitPrice*qty
            writer.writerow([prodID, prodName, unitPrice, qty, totalPrice])
            print(fin)
            fin.close()
