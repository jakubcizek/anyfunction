from anyfunction import anyFunction

cisla = [0,1,2,3,4,5,6,7,8,9]
suda = anyFunction(cisla, "odstran licha cisla", list)
print(suda)

soucet = anyFunction(cisla, "spočítej cisla", int)
print(soucet)

zviratka = ["pes", "kočka", "slon", "orel", "velryba"]
domaci = anyFunction(zviratka, "vyber pouze domaci zvirata", list)
print(domaci)

veta = "Dobrý den, jmenuji se Luboš Čmelák a někde jsem ztratil tkaničky od bot."
anglicky = anyFunction(veta, "preloz text do anglictiny", str)
print(anglicky)