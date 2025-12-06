from anyfunction import anyFunction

cisla = [0,1,2,3,4,5,6,7,8,9]
nejvetsi = anyFunction(cisla, "které číslo je největší", int, model="gpt-5-nano")
print(f"Největší číslo v poli cisla je: {nejvetsi}")