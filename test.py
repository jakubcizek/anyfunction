from anyfunction import anyFunction as af, Run

'''
Nastaveni ve skriptu anyfunction.py
API_KEY: API klic pro platformu OpenAI (pripadne neni problem upravit pro jineho providera)
MODEL: Vychozi model, pokud neni nastaveni explicitne ve volani funkce anyFunction

Jednoduche volani:
ODPOVED = anyFunction(VSTUP, PROMPT, TYP_ODPOVEDI)

Volani s vynucenym modelem:
ODPOVED = anyFunction(VSTUP, PROMPT, TYP_ODPOVEDI, model="gpt-5-nano")

Volani s lokalnim spustenim kodu (specialni rezim, kdy i model vi, ze ma generovat kod v Pythonu, ktery spustime lokalne):
anyFunction(VSTUP, PROMPT, Run)

'''

cisla = [0,1,2,3,4,5,6,7,8,9]
suda = af(cisla, "odstran licha cisla", list, model = "gpt-5-nano")
print(suda)

serazena = af(cisla, "serad od nejvetsiho", list)
print(serazena)

zviratka = ["pes", "kočka", "slon", "orel", "velryba"]
domaci = af(zviratka, "vyber pouze domaci zvirata", list)
print(domaci)

veta = "Dobrý den, jmenuji se Luboš Čmelák a někde jsem ztartil tkaničky od bot."
anglicky = af(veta, "preloz text do anglcitiny", str)
print(anglicky)

data = {
    "klic_1": True,
    "klic_2": 4569,
    "klic_3": [1,2,3,4,5]
}
prejmenovano = af(data, "Prejmenuj klice podle formatu klic_0X", dict)
print(prejmenovano)

af(None, "Kazdou sekundu vypis na novy radek a odlisnou barvou aktualni cas ve formatu HH:MM:SS. Po deseti skonci", Run)
