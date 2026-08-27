ALERTS = {"English":"Flood emergency detected in Zone A. Please evacuate using the designated route to the assigned shelter.", "Telugu":"జోన్ A లో వరద అత్యవసర పరిస్థితి. కేటాయించిన ఆశ్రయానికి సూచించిన మార్గంలో ఖాళీ చేయండి.", "Hindi":"जोन A में बाढ़ आपातकाल। निर्धारित आश्रय तक निर्दिष्ट मार्ग से जाएं।"}
def generate(language="English"): return ALERTS.get(language, ALERTS["English"])
